import json
import asyncio
from firebase_functions import https_fn
from agents import Agent, Runner, trace, RunHooks, RunContextWrapper, Usage, Tool
from datetime import datetime, timedelta
import re
import uuid
from typing import Any
from .utils.header import get_cors_headers
from services.user_service import UserService
from services.chat_session_service import ChatSessionService
from function_tools.chat_tools import save_chat_message_tool, get_chat_messages_tool
from function_tools.nutrition_tools import save_nutrition_entry_tool, get_nutrition_entry_tool
from services.chat_message_service import ChatMessageService
from function_tools.get_nutrition_search_tool import get_nutrition_search_tool
from function_tools.get_nutrition_details_tool import get_nutrition_details_tool
from function_tools.calculate_nutrition_summary_tool import calculate_nutrition_summary_tool


# ライフサイクルフック定義
class NutritionHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    def _usage_to_str(self, usage: Usage) -> str:
        return f"{usage.requests} requests, {usage.input_tokens} input tokens, {usage.output_tokens} output tokens, {usage.total_tokens} total tokens"

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: エージェント {agent.name} 開始. 使用量: {self._usage_to_str(context.usage)}"
        )

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: エージェント {agent.name} 終了. 使用量: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: ツール {tool.name} 開始. 使用量: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        # result が文字列以外の場合は文字列化してからスライス
        result_str = result if isinstance(result, str) else str(result)
        print(
            f"### {self.event_counter}: ツール {tool.name} 終了. 結果: {result_str[:50]}.... 使用量: {self._usage_to_str(context.usage)}"
        )

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: {from_agent.name} から {to_agent.name} へハンドオフ. 使用量: {self._usage_to_str(context.usage)}"
        )

# フックインスタンス作成
nutrition_hooks = NutritionHooks()

main_agent = Agent(
    name="MainAgent",
    model="gpt-4o-mini",
    instructions="""
    ユーザーとの自然な対話を行うトップレベルエージェントです。
    必要に応じてチャット履歴や栄養記録の取得・保存ツールを呼び出し、
    ユーザーの健康管理をサポートしてください。
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
@https_fn.on_request(timeout_sec=540)
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
    user_id = "5e550382-1cfb-4d30-8403-33e63548b5db"
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        ChatSessionService().create_session(user_id)

    print(f"user_id: {user_id}, session_id: {session_id}")

    # メッセージ形式 - システムメッセージにCookie情報を含める
    formatted_messages = [
        {"role": "system", "content": f"#SYSTEM_DATA\nuser_id: {user_id}, session_id: {session_id}\n#END_SYSTEM_DATA"},
        {"role": "user", "content": prompt}
    ]

    ChatMessageService().save_message(user_id, session_id, "user", prompt)

    try:
        result = asyncio.run(
            Runner.run(
                main_agent,
                formatted_messages,
                hooks=nutrition_hooks
            )
        )

        # エージェントの応答を取得
        agent_response = result.final_output

        ChatMessageService().save_message(user_id, session_id, "agent", agent_response)

        # セッションIDをCookieにセット
        headers_with_cookie = headers.copy()
        # セッションIDクッキーを1週間有効な永続化クッキーとして設定
        expires = (datetime.utcnow() + timedelta(days=7)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers_with_cookie["Set-Cookie"] = (
            f"session_id={session_id}; Path=/; Expires={expires}; HttpOnly; SameSite=None; Secure"
        )
        return https_fn.Response(
            json.dumps({"message": agent_response}),
            status=200,
            headers=headers_with_cookie
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"message": "処理中にエラーが発生しました。", "error": str(e)}),
            status=500,
            headers=headers
        )