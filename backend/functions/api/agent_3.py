import json
import asyncio
from firebase_functions import https_fn
from agents import Agent, Runner, trace
from repositories.chat_sessions_repository import ChatSessionsRepository
from repositories.chats_repository import ChatsRepository
from repositories.nutrition_entries_repository import NutritionEntriesRepository
from datetime import datetime
import re
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union, Literal


# コンテキストモデル
class NutritionItem(BaseModel):
    food_item: str
    quantity_desc: str
    
    model_config = {
        "extra": "forbid"
    }

class Nutrients(BaseModel):
    calories: float
    protein: float
    fat: Optional[float] = None
    carbs: Optional[float] = None
    # 他の栄養素も必要に応じて追加
    
    model_config = {
        "extra": "forbid"
    }

class MealData(BaseModel):
    meal_type: Literal["breakfast", "lunch", "dinner", "snack", "late_night_meal"]
    items: List[NutritionItem]
    nutrients: Nutrients
    
    model_config = {
        "extra": "forbid"
    }

class CollectedItem(BaseModel):
    food_item: str
    quantity_desc: Optional[str] = None
    meal_type: Optional[str] = None
    
    model_config = {
        "extra": "forbid"
    }

class NutritionData(BaseModel):
    status: Literal["collecting", "completed"]
    meals: Optional[List[MealData]] = None
    missing_info: Optional[List[str]] = None
    collected_items: Optional[List[CollectedItem]] = None
    total_nutrients: Optional[Nutrients] = None
    summary: Optional[str] = None
    
    model_config = {
        "extra": "forbid"
    }

class ChatMessage(BaseModel):
    role: str
    content: str
    
    model_config = {
        "extra": "forbid"
    }

class NutritionContext(BaseModel):
    user_id: str
    session_id: str
    previous_messages: List[ChatMessage] = []
    nutrition_data: Optional[NutritionData] = None
    
    model_config = {
        "extra": "forbid"
    }


from .utils.cors import get_cors_headers


# エージェント定義
formatter_agent = Agent(
    name="MessageFormatterAgent",
    model="gpt-3.5-turbo",
    instructions="""
    あなたは栄養計算結果を人間に分かりやすく伝えるスペシャリストです。
    入力された栄養計算結果と食事データから、ユーザーに最適な形で情報を伝えてください。

    以下の内容を必ず含めてください：
    1. 各食事（朝食/昼食/夕食など）の栄養素の概要
    2. トータルカロリーとタンパク質量
    3. 食事のバランスに関する簡潔なアドバイス
    4. 励ましのメッセージ

    専門用語を避け、親しみやすく、ポジティブな言葉で伝えてください。
    箇条書きで改行して端的に伝えてください。

    重要: レスポンスは必ずユーザー向けメッセージのみとし、システムデータや技術的な内容を含めないでください。
    """
)

nutrition_agent = Agent(
    name="NutritionConversationalAgent",
    model="gpt-3.5-turbo",
    instructions="""
    あなたは栄養計算の専門家です。ユーザーとの自然な会話を通じて食事情報を収集し、栄養計算を行います。

    【行動指針】
    1. ユーザーが食事内容を伝えてきたら、不足情報（食材・量など）があれば質問してください
    2. 十分な情報が集まったら栄養計算を行い、結果を日本語で説明してください
    3. 常に親切で会話的な応答を心がけてください
    4. meal_typeは必ず以下のいずれかを使用してください：breakfast/lunch/dinner/snack/late_night_meal
    5. 過去の会話履歴を参照し、コンテキストを維持してください
    6. 既に回答済みの質問には「了解しました」などの重複した応答を避けてください
    7. ユーザーが既に提供した情報（食材、量、調理方法など）は再度質問せず、足りない情報のみ質問してください

    【必須: システムデータの提供】
    あなたの応答は必ず以下の2つの部分に分けてください:

    1. ユーザー向けメッセージ - 通常の会話形式で説明
    2. システム向けデータ - 以下のフォーマットで記述（このブロックは必ず含めてください）

    #SYSTEM_DATA
    {"status": "collecting", "missing_info": [], "collected_items": []}
    #END_SYSTEM_DATA

    もし十分な情報が集まっていない場合は上記のように "collecting" ステータスを返してください。
    十分な情報が集まって栄養計算ができる場合は、以下のようなフォーマットでデータを提供してください:

    #SYSTEM_DATA
    {
      "status": "completed",
      "meals": [
        {
          "meal_type": "breakfast",
          "items": [
            {"food_item": "卵白", "quantity_desc": "10個"}
          ],
          "nutrients": {"calories": 170, "protein": 35, "fat": 0, "carbs": 0}
        }
      ],
      "total_nutrients": {"calories": 170, "protein": 35, "fat": 0, "carbs": 0}
    }
    #END_SYSTEM_DATA

    【重要】システムデータブロックは必ず含めてください。常に応答にシステムデータブロックを含めるようにしてください。
    """,
    handoffs=[formatter_agent]
)

# HTTP関数
@https_fn.on_request(timeout_sec=540)
def agent(request):
    headers = get_cors_headers()
    # OPTIONS プレフライト対応
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    user_id = request.headers.get("X-User-ID", "5e550382-1cfb-4d30-8403-33e63548b5db")

    # セッションIDのチェック／作成
    session_id = request.cookies.get("session_id")
    chat_sessions = ChatSessionsRepository()
    if not session_id:
        session_id = chat_sessions.create_session(user_id)
        print(f"新しいセッション作成: {session_id}")
    else:
        print(f"既存セッション使用: {session_id}")

    # リクエストボディからプロンプトを取得
    body = request.get_json(silent=True) or {}
    prompt = body.get("prompt")
    if not prompt:
        return https_fn.Response(
            json.dumps({"error": "prompt フィールドが必要です"}),
            status=400,
            headers=headers
        )

    print(f"受信プロンプト: {prompt}")

    # ユーザー発言を保存
    chats = ChatsRepository()
    chats.create_message(user_id, session_id, "user", prompt)

    # 過去のチャット履歴を直接取得して使用
    try:
        # 過去の会話を取得（最新3件）
        previous_messages = chats.get_messages(user_id, session_id, 4)
        formatted_messages = []
        
        # 時間順にソート
        sorted_messages = sorted(previous_messages[:-1], key=lambda x: x.get("created_at", ""))
        for msg in sorted_messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("message_text", "")
            })
            
        # 最後に現在のプロンプトを追加
        formatted_messages.append({"role": "user", "content": prompt})
        
        print(f"エージェントに渡すメッセージ数: {len(formatted_messages)}")
    except Exception as e:
        print(f"履歴取得エラー: {e}")
        # エラー時は現在のプロンプトのみ使用
        formatted_messages = [{"role": "user", "content": prompt}]

    # エージェント実行（会話ID生成）
    conversation_id = f"{user_id}_{session_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    print(f"会話ID: {conversation_id}")
    
    try:
        with trace("nutrition-workflow", group_id=conversation_id):
            # エージェント実行
            print("エージェントの実行を開始します...")
            result = asyncio.run(
                Runner.run(nutrition_agent, formatted_messages)
            )
            print("エージェントの実行が完了しました")
            
            # 応答を保存
            agent_response = result.final_output
            chats.create_message(user_id, session_id, "agent", agent_response)
            
            # デバッグ用にエージェント応答全体をログに出力
            print(f"エージェント応答全体: {agent_response[:100]}...")
            
            # システムデータを抽出
            system_data_pattern = r'#SYSTEM_DATA\s*([\s\S]*?)\s*#END_SYSTEM_DATA'
            system_data_match = re.search(system_data_pattern, agent_response)
            print(f"システムデータパターンが見つかりました: {system_data_match is not None}")
            
            if system_data_match:
                try:
                    system_data_text = system_data_match.group(1).strip()
                    print(f"抽出されたシステムデータテキスト: {system_data_text[:100]}...")
                    system_data = json.loads(system_data_text)
                    user_message = re.sub(system_data_pattern, '', agent_response).strip()
                    
                    print(f"システムデータステータス: {system_data.get('status')}")
                    
                    # 栄養データが完了していれば保存
                    if system_data.get("status") == "completed" and "meals" in system_data:
                        print(f"栄養データ保存開始: {len(system_data['meals'])}件")
                        
                        # 栄養データを保存
                        nutrients_repo = NutritionEntriesRepository()
                        for meal in system_data["meals"]:
                            meal_type = meal["meal_type"]
                            items = meal["items"]
                            
                            print(f"保存する食事: {meal_type}, アイテム数: {len(items)}")
                            
                            nutrients_repo.create_entry(
                                user_id=user_id,
                                entry_date=datetime.now().strftime("%Y-%m-%d"),
                                meal_type=meal_type,
                                food_item=", ".join([item["food_item"] for item in items]),
                                quantity_desc=", ".join([item["quantity_desc"] for item in items]),
                                nutrients=meal["nutrients"]
                            )
                            print(f"保存完了: meal_type={meal_type}")
                        
                        # formatter_agentを呼び出して応答を整形
                        print("メッセージ整形エージェントを呼び出します...")
                        formatter_input = [{"role": "user", "content": user_message}]
                        formatter_result = asyncio.run(
                            Runner.run(formatter_agent, formatter_input)
                        )
                        formatted_message = formatter_result.final_output
                        print("メッセージ整形が完了しました")
                        
                        # 整形されたメッセージとデータ保存通知を返す
                        final_output = formatted_message + "\n\n✅ 栄養データを保存しました！"
                    else:
                        # 計算未完了時はシステムデータを除いたメッセージのみ返す
                        print(f"栄養データ計算未完了: status={system_data.get('status')}")
                        final_output = user_message
                except json.JSONDecodeError as e:
                    # JSONパースエラー時は元のメッセージからシステムデータ部分のみ除去
                    print(f"JSONパースエラー: {e}")
                    final_output = re.sub(system_data_pattern, '', agent_response).strip()
            else:
                # システムデータが見つからない場合は、デフォルトのシステムデータを生成して除去
                print("システムデータが見つかりません。デフォルトデータを使用します。")
                default_system_data = {
                    "status": "collecting",
                    "missing_info": ["食事内容"],
                    "collected_items": []
                }
                
                # 次回のためにシステムデータを含む完全な応答をリポジトリに保存
                full_response = f"{agent_response}\n\n#SYSTEM_DATA\n{json.dumps(default_system_data, ensure_ascii=False)}\n#END_SYSTEM_DATA"
                chats.create_message(user_id, session_id, "system", full_response)
                
                # ユーザーには元のメッセージをそのまま返す
                final_output = agent_response
            
            print(f"最終出力: {final_output[:100]}...")
            
            return https_fn.Response(
                json.dumps({"message": final_output, "session_id": session_id}),
                status=200,
                headers=headers
            )
                
    except Exception as e:
        error_message = f"エージェント実行エラー: {str(e)}"
        print(error_message)
        import traceback
        print(traceback.format_exc())
        
        # エラー時のフォールバック応答
        fallback_response = "申し訳ありません。処理中にエラーが発生しました。もう一度お試しください。"
        
        return https_fn.Response(
            json.dumps({"message": fallback_response, "error": str(e), "session_id": session_id}),
            status=500,
            headers=headers
        )
