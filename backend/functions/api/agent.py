import json
import asyncio
import os
from firebase_functions import https_fn, params
from agents import Agent, Runner, trace, RunHooks, RunContextWrapper, Usage, Tool
from datetime import datetime, timedelta
import re
import uuid
from typing import Any, Dict, List
from .utils.header import get_cors_headers
from services.user_service import UserService
from services.chat_session_service import ChatSessionService
from function_tools.chat_tools import save_chat_message_tool, get_chat_messages_tool
from function_tools.nutrition_tools import save_nutrition_entry_tool, get_nutrition_entry_tool
from services.chat_message_service import ChatMessageService
from function_tools.get_nutrition_search_tool import get_nutrition_search_tool
from function_tools.get_nutrition_details_tool import get_nutrition_details_tool
from function_tools.calculate_nutrition_summary_tool import calculate_nutrition_summary_tool


# 詳細トレーシング用フック定義
class DetailedNutritionHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0
        self.tool_calls = []
        self.llm_generations = []
        self.errors = []

    def _usage_to_str(self, usage: Usage) -> str:
        return f"{usage.requests} requests, {usage.input_tokens} input tokens, {usage.output_tokens} output tokens, {usage.total_tokens} total tokens"

    def _log_with_timestamp(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"🚀 ### {self.event_counter}: エージェント {agent.name} 開始"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")
        self._log_with_timestamp(f"🔧 利用可能ツール: {[tool.name for tool in agent.tools]}")

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"🏁 ### {self.event_counter}: エージェント {agent.name} 終了"
        )
        self._log_with_timestamp(f"📊 最終使用量: {self._usage_to_str(context.usage)}")
        self._log_with_timestamp(f"📝 最終出力: {str(output)[:200]}...")

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"🔨 ### {self.event_counter}: ツール {tool.name} 開始"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")
        
        # ツール呼び出し情報を記録（引数も含める）
        tool_call_info = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "agent_name": agent.name,
            "event_counter": self.event_counter,
            "status": "started"
        }
        
        # ツールの引数情報を取得（可能な場合）
        try:
            if hasattr(tool, 'function') and hasattr(tool.function, '__name__'):
                tool_call_info["function_name"] = tool.function.__name__
            if hasattr(tool, 'description'):
                tool_call_info["description"] = tool.description
        except Exception as e:
            self._log_with_timestamp(f"⚠️ ツール情報取得エラー: {str(e)}")
        
        self.tool_calls.append(tool_call_info)
        self._log_with_timestamp(f"📋 ツール詳細: {tool_call_info}")
        
        # 利用可能なツール一覧も表示
        available_tools = [t.name for t in agent.tools]
        self._log_with_timestamp(f"🔧 エージェントの利用可能ツール: {available_tools}")
        
        # 現在のツールが利用可能ツールに含まれているかチェック
        if tool.name not in available_tools:
            self._log_with_timestamp(f"⚠️ 警告: ツール '{tool.name}' はエージェントの利用可能ツールリストにありません！")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        result_str = result if isinstance(result, str) else str(result)
        self._log_with_timestamp(
            f"✅ ### {self.event_counter}: ツール {tool.name} 終了"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")
        self._log_with_timestamp(f"📤 結果: {result_str[:200]}...")
        
        # ツール呼び出し完了情報を記録
        tool_call_info = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool.name,
            "agent_name": agent.name,
            "event_counter": self.event_counter,
            "status": "completed",
            "result_preview": result_str[:100]
        }
        self.tool_calls.append(tool_call_info)

    async def on_generation_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"🧠 ### {self.event_counter}: LLM生成開始 (エージェント: {agent.name})"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")

    async def on_generation_end(self, context: RunContextWrapper, agent: Agent, output: str) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"💭 ### {self.event_counter}: LLM生成終了 (エージェント: {agent.name})"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")
        self._log_with_timestamp(f"📝 生成内容: {output[:200]}...")
        
        # LLM生成情報を記録
        generation_info = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent.name,
            "event_counter": self.event_counter,
            "output_preview": output[:100]
        }
        self.llm_generations.append(generation_info)

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"🔄 ### {self.event_counter}: {from_agent.name} から {to_agent.name} へハンドオフ"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")

    async def on_error(self, context: RunContextWrapper, error: Exception) -> None:
        self.event_counter += 1
        self._log_with_timestamp(
            f"❌ ### {self.event_counter}: エラー発生: {str(error)}"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")
        
        # エラー情報を記録
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "event_counter": self.event_counter,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        self.errors.append(error_info)

    def get_summary(self) -> Dict[str, Any]:
        """実行サマリーを取得"""
        return {
            "total_events": self.event_counter,
            "tool_calls": self.tool_calls,
            "llm_generations": self.llm_generations,
            "errors": self.errors,
            "tool_call_count": len([tc for tc in self.tool_calls if tc["status"] == "completed"]),
            "generation_count": len(self.llm_generations),
            "error_count": len(self.errors)
        }

    def analyze_prompt_for_tools(self, prompt: str) -> Dict[str, Any]:
        """プロンプトを分析してどのツールが必要かを判断"""
        analysis = {
            "prompt": prompt,
            "expected_tools": [],
            "prompt_type": "unknown",
            "keywords": []
        }
        
        prompt_lower = prompt.lower()
        
        # 食事記録関連のキーワード
        food_keywords = ["食べた", "食事", "朝食", "昼食", "夕食", "おやつ", "飲んだ", "摂取", "食べました", "飲みました"]
        # 栄養情報取得関連のキーワード
        nutrition_keywords = ["栄養", "カロリー", "タンパク質", "炭水化物", "脂質", "ビタミン", "ミネラル"]
        # チャット履歴関連のキーワード
        chat_keywords = ["履歴", "過去", "前回", "以前", "記録", "ログ"]
        # 検索関連のキーワード
        search_keywords = ["検索", "探す", "調べる", "見つける", "情報"]
        
        # キーワード分析
        found_keywords = []
        if any(keyword in prompt_lower for keyword in food_keywords):
            analysis["expected_tools"].append("save_nutrition_entry_tool")
            analysis["prompt_type"] = "food_logging"
            found_keywords.extend([k for k in food_keywords if k in prompt_lower])
            
        if any(keyword in prompt_lower for keyword in nutrition_keywords):
            analysis["expected_tools"].extend(["get_nutrition_search_tool", "get_nutrition_details_tool", "calculate_nutrition_summary_tool"])
            if analysis["prompt_type"] == "unknown":
                analysis["prompt_type"] = "nutrition_inquiry"
            found_keywords.extend([k for k in nutrition_keywords if k in prompt_lower])
            
        if any(keyword in prompt_lower for keyword in chat_keywords):
            analysis["expected_tools"].append("get_chat_messages_tool")
            if analysis["prompt_type"] == "unknown":
                analysis["prompt_type"] = "chat_history"
            found_keywords.extend([k for k in chat_keywords if k in prompt_lower])
            
        if any(keyword in prompt_lower for keyword in search_keywords):
            analysis["expected_tools"].append("get_nutrition_search_tool")
            found_keywords.extend([k for k in search_keywords if k in prompt_lower])
        
        # 栄養記録取得のパターン
        if any(phrase in prompt_lower for phrase in ["今日の栄養", "栄養記録", "摂取量", "栄養状況"]):
            analysis["expected_tools"].append("get_nutrition_entry_tool")
            if analysis["prompt_type"] == "unknown":
                analysis["prompt_type"] = "nutrition_status"
        
        analysis["keywords"] = list(set(found_keywords))
        analysis["expected_tools"] = list(set(analysis["expected_tools"]))  # 重複除去
        
        return analysis

# フックインスタンス作成
nutrition_hooks = DetailedNutritionHooks()

main_agent = Agent(
    name="MainAgent",
    model="gpt-4o-mini",
    instructions="""
    ユーザーとの自然な対話を行うトップレベルエージェントです。
    
    重要な動作ルール：
    1. 食事内容の報告時の処理：
       - ユーザーが食事内容を報告した場合、必ずsave_nutrition_entry_toolを使用して栄養記録を保存してください
       - 栄養情報APIが利用できない場合は、以下の推定値を使用してください：
         * ご飯100g: カロリー130kcal, タンパク質2.2g, 炭水化物29g, 脂質0.3g
         * 卵1個: カロリー70kcal, タンパク質6g, 炭水化物0.5g, 脂質5g
         * パン1枚: カロリー160kcal, タンパク質6g, 炭水化物28g, 脂質3g
       - 各食材について1回ずつsave_nutrition_entry_toolを呼び出してください（重複呼び出し禁止）
       - 保存後に「栄養記録を保存しました」と報告してください
    
    2. 栄養情報の問い合わせ時の処理：
       - 栄養情報を聞かれた場合は、まずget_nutrition_search_toolで検索を試してください
       - 検索が失敗した場合のみ、一般的な栄養価を回答してください
       - 詳細情報が必要な場合はget_nutrition_details_toolを使用してください
    
    3. 栄養記録の確認時の処理：
       - 「今日の栄養」「栄養摂取量」などの問い合わせには、get_nutrition_entry_toolを使用してください
       - 複数の記録がある場合は、calculate_nutrition_summary_toolで合計を計算してください
    
    4. チャット履歴の確認時の処理：
       - 「履歴」「過去の会話」などの問い合わせには、get_chat_messages_toolを使用してください
    
    5. ツール使用の原則：
       - 同じツールを連続して複数回呼び出さないでください
       - エラーが発生した場合は、1回だけリトライしてください
       - ツールが失敗した場合は、推定値や一般的な情報で回答してください
    
    処理フロー例：
    - 食事報告 → 推定値で栄養計算 → save_nutrition_entry_toolで保存（各食材1回ずつ） → 保存完了を報告
    - 栄養問い合わせ → get_nutrition_search_toolで検索 → 結果を回答（失敗時は推定値）
    - 栄養記録確認 → get_nutrition_entry_toolで取得 → 結果を表示
    """,
    tools=[
        save_nutrition_entry_tool,
        get_nutrition_entry_tool,
        get_chat_messages_tool,
        get_nutrition_search_tool,
        get_nutrition_details_tool,
        calculate_nutrition_summary_tool
    ]
)

# HTTP関数
@https_fn.on_request(timeout_sec=540, secrets=[params.SecretParam("OPENAI_API_KEY")])
def agent(request):
    headers = get_cors_headers()
    # OPTIONS プレフライト対応
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    # リクエストボディからプロンプトを取得
    body = request.get_json(silent=True) or {}
    prompt = body.get("prompt")
    if not prompt:
        return https_fn.Response(
            json.dumps({"error": "prompt フィールドが必要です"}),
            status=400,
            headers=headers
        )

    # Cookieヘッダーを取得
    user_id = "118e326e-66a5-41ce-9ec2-b5553d134f81"
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        ChatSessionService().create_session(user_id)

    print(f"🔍 リクエスト詳細: user_id={user_id}, session_id={session_id}")
    print(f"📝 ユーザープロンプト: {prompt}")

    # プロンプト分析を実行
    prompt_analysis = nutrition_hooks.analyze_prompt_for_tools(prompt)
    print(f"\n🔍 === プロンプト分析結果 ===")
    print(f"📝 プロンプトタイプ: {prompt_analysis['prompt_type']}")
    print(f"🔑 検出キーワード: {prompt_analysis['keywords']}")
    print(f"🔧 期待されるツール: {prompt_analysis['expected_tools']}")
    print(f"🔍 === 分析結果終了 ===\n")

    # メッセージ形式 - システムメッセージにCookie情報を含める
    formatted_messages = [
        {"role": "system", "content": f"#SYSTEM_DATA\nuser_id: {user_id}, session_id: {session_id}\n#END_SYSTEM_DATA"},
        {"role": "user", "content": prompt}
    ]

    print(f"💾 ユーザーメッセージを保存中...")
    ChatMessageService().save_message(user_id, session_id, "user", prompt)
    print(f"✅ ユーザーメッセージ保存完了")

    # フックをリセット（新しいリクエストのため）
    nutrition_hooks.event_counter = 0
    nutrition_hooks.tool_calls = []
    nutrition_hooks.llm_generations = []
    nutrition_hooks.errors = []

    try:
        print(f"🚀 エージェント実行開始...")
        
        # トレーシング付きでエージェントを実行
        with trace("Nutrition Agent Workflow", metadata={"user_id": user_id, "session_id": session_id, "prompt": prompt[:100]}):
            result = asyncio.run(
                Runner.run(
                    main_agent,
                    formatted_messages,
                    hooks=nutrition_hooks
                )
            )

        # エージェントの応答を取得
        agent_response = result.final_output
        print(f"🤖 Agent応答: {agent_response[:100]}...")

        # 実行サマリーを出力
        summary = nutrition_hooks.get_summary()
        print(f"\n📊 === 実行サマリー ===")
        print(f"📈 総イベント数: {summary['total_events']}")
        print(f"🔨 ツール呼び出し数: {summary['tool_call_count']}")
        print(f"🧠 LLM生成数: {summary['generation_count']}")
        print(f"❌ エラー数: {summary['error_count']}")
        
        # 期待されるツールと実際のツールの比較
        actual_tools = [tc['tool_name'] for tc in summary['tool_calls'] if tc['status'] == 'completed']
        expected_tools = prompt_analysis['expected_tools']
        
        print(f"\n🔍 === ツール呼び出し分析 ===")
        print(f"🎯 期待されるツール: {expected_tools}")
        print(f"✅ 実際に呼び出されたツール: {actual_tools}")
        
        # ツール呼び出しの適切性を分析
        if expected_tools:
            matched_tools = set(actual_tools) & set(expected_tools)
            missing_tools = set(expected_tools) - set(actual_tools)
            unexpected_tools = set(actual_tools) - set(expected_tools)
            
            print(f"✅ 期待通りに呼び出されたツール: {list(matched_tools)}")
            if missing_tools:
                print(f"⚠️ 期待されたが呼び出されなかったツール: {list(missing_tools)}")
            if unexpected_tools:
                print(f"🔄 期待されていなかったが呼び出されたツール: {list(unexpected_tools)}")
                
            # 適切性スコア計算
            if expected_tools:
                appropriateness_score = len(matched_tools) / len(expected_tools) * 100
                print(f"📊 ツール呼び出し適切性スコア: {appropriateness_score:.1f}%")
        else:
            print(f"ℹ️ このプロンプトではツール呼び出しは期待されていませんでした")
            if actual_tools:
                print(f"🔄 しかし以下のツールが呼び出されました: {actual_tools}")
        
        print(f"🔍 === ツール分析終了 ===")
        
        if summary['tool_calls']:
            print(f"\n🔧 ツール呼び出し詳細:")
            for i, tool_call in enumerate(summary['tool_calls'], 1):
                print(f"  {i}. {tool_call['tool_name']} ({tool_call['status']}) - {tool_call['timestamp']}")
        
        if summary['errors']:
            print(f"\n⚠️ エラー詳細:")
            for i, error in enumerate(summary['errors'], 1):
                print(f"  {i}. {error['error_type']}: {error['error_message']}")
        
        print(f"📊 === サマリー終了 ===\n")

        print(f"💾 Agentメッセージを保存中...")
        ChatMessageService().save_message(user_id, session_id, "agent", agent_response)
        print(f"✅ Agentメッセージ保存完了")

        # セッションIDをCookieにセット
        headers_with_cookie = headers.copy()
        # セッションIDクッキーを1週間有効な永続化クッキーとして設定
        expires = (datetime.utcnow() + timedelta(days=7)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers_with_cookie["Set-Cookie"] = (
            f"session_id={session_id}; Path=/; Expires={expires}; HttpOnly; SameSite=None; Secure"
        )
        
        # レスポンスにサマリー情報も含める（デバッグ用）
        response_data = {
            "message": agent_response,
            "debug_info": {
                "tool_calls": summary['tool_call_count'],
                "llm_generations": summary['generation_count'],
                "errors": summary['error_count'],
                "total_events": summary['total_events'],
                "prompt_analysis": {
                    "type": prompt_analysis['prompt_type'],
                    "keywords": prompt_analysis['keywords'],
                    "expected_tools": prompt_analysis['expected_tools']
                },
                "tool_analysis": {
                    "expected_tools": expected_tools,
                    "actual_tools": actual_tools,
                    "matched_tools": list(set(actual_tools) & set(expected_tools)) if expected_tools else [],
                    "missing_tools": list(set(expected_tools) - set(actual_tools)) if expected_tools else [],
                    "unexpected_tools": list(set(actual_tools) - set(expected_tools)) if expected_tools else []
                }
            }
        }
        
        return https_fn.Response(
            json.dumps(response_data),
            status=200,
            headers=headers_with_cookie
        )
    except Exception as e:
        print(f"❌ Agent実行エラー: {str(e)}")
        print(f"❌ エラータイプ: {type(e).__name__}")
        
        # エラー時サマリーを出力
        summary = nutrition_hooks.get_summary()
        print(f"\n📊 === エラー時サマリー ===")
        print(f"📈 総イベント数: {summary['total_events']}")
        print(f"🔨 ツール呼び出し数: {summary['tool_call_count']}")
        print(f"❌ エラー数: {summary['error_count']}")
        if summary['errors']:
            print(f"⚠️ 記録されたエラー:")
            for error in summary['errors']:
                print(f"  - {error['error_type']}: {error['error_message']}")
        print(f"📊 === エラー時サマリー終了 ===\n")
        
        return https_fn.Response(
            json.dumps({
                "message": "処理中にエラーが発生しました。", 
                "error": str(e),
                "debug_info": {
                    "error_type": type(e).__name__,
                    "tool_calls": summary['tool_call_count'],
                    "errors": summary['error_count']
                }
            }),
            status=500,
            headers=headers
        )