import json
import asyncio
from firebase_functions import https_fn
from agents import Agent, Runner, trace, handoff
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


# 共通のHTTP関連関数
def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }


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

    【レスポンスフォーマット - 必須】
    あなたの応答は必ず以下の2つの部分に分けてください：

    1. ユーザー向けメッセージ - 通常の会話形式で説明
    2. システム向けデータ - 以下のフォーマットで記述

    #SYSTEM_DATA
    {"status": "collecting" または "completed", ...必要なデータ}
    #END_SYSTEM_DATA
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

    # （開発中はダミーの）ユーザーIDを取得
    user_id = "5e550382-1cfb-4d30-8403-33e63548b5db"

    # セッションIDのチェック／作成
    session_id = request.cookies.get("session_id")
    chat_sessions = ChatSessionsRepository()
    if not session_id:
        session_id = chat_sessions.create_session(user_id)

    # リクエストボディからプロンプトを取得
    body = request.get_json(silent=True) or {}
    prompt = body.get("prompt")
    if not prompt:
        return https_fn.Response(
            json.dumps({"error": "prompt フィールドが必要です"}),
            status=400,
            headers=headers
        )

    # ユーザー発言を保存
    chats = ChatsRepository()
    chats.create_message(user_id, session_id, "user", prompt)

    # 過去のチャット履歴を取得（コンテキスト維持のため）
    previous_messages = chats.get_messages(user_id, session_id)
    
    # 入力メッセージリストの作成
    formatted_messages = []
    for msg in previous_messages:
        formatted_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("message_text", "")
        })

    # 現在のプロンプトを追加
    formatted_messages.append({"role": "user", "content": prompt})

    # エージェント実行（会話ID生成）
    conversation_id = f"{user_id}_{session_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        with trace("nutrition-workflow", group_id=conversation_id):
            # 非同期処理を同期的に実行する
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            result = loop.run_until_complete(
                Runner.run(nutrition_agent, formatted_messages)
            )
            
            # 応答を保存
            agent_response = result.final_output
            chats.create_message(user_id, session_id, "agent", agent_response)
            
            # デバッグ用にエージェント応答全体をログに出力
            print(f"エージェント応答全体: {agent_response}")
            
            # システムデータを抽出
            system_data_pattern = r'#SYSTEM_DATA\s*([\s\S]*?)\s*#END_SYSTEM_DATA'
            system_data_match = re.search(system_data_pattern, agent_response)
            print(f"system_data_match: {system_data_match}")
            
            if system_data_match:
                try:
                    system_data_text = system_data_match.group(1).strip()
                    print(f"抽出されたシステムデータ: {system_data_text}")
                    system_data = json.loads(system_data_text)
                    user_message = re.sub(system_data_pattern, '', agent_response).strip()
                    
                    # 栄養データが完了していれば保存
                    if system_data.get("status") == "completed" and "meals" in system_data:
                        # 短い処理で整形するのでformatter_agentは使わない
                        final_output = user_message + "\n\n✅ 栄養データを保存しました！"
                        
                        # 栄養データを保存
                        nutrients_repo = NutritionEntriesRepository()
                        for meal in system_data["meals"]:
                            meal_type = meal["meal_type"]
                            items = meal["items"]
                            
                            nutrients_repo.create_entry(
                                user_id=user_id,
                                entry_date=datetime.now().strftime("%Y-%m-%d"),
                                meal_type=meal_type,
                                food_item=", ".join([item["food_item"] for item in items]),
                                quantity_desc=", ".join([item["quantity_desc"] for item in items]),
                                nutrients=meal["nutrients"]
                            )
                    else:
                        # 計算未完了時はシステムデータを除いたメッセージのみ返す
                        final_output = user_message
                except json.JSONDecodeError as e:
                    # JSONパースエラー時は元のメッセージからシステムデータ部分のみ除去
                    final_output = re.sub(system_data_pattern, '', agent_response).strip()
            else:
                # システムデータが見つからない場合は元のメッセージをそのまま使用
                final_output = agent_response
            
            return https_fn.Response(
                json.dumps({"message": final_output, "session_id": session_id}),
                status=200,
                headers=headers
            )
                
    except Exception as e:
        print(f"エージェント実行エラー: {e}")
        return https_fn.Response(
            json.dumps({"error": "処理中にエラーが発生しました"}),
            status=500,
            headers=headers
        )