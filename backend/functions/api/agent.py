import json
import asyncio
from firebase_functions import https_fn
from agents import Agent, Runner, trace, RunHooks, RunContextWrapper, Usage, Tool
from datetime import datetime
import re
from typing import Any
from .utils.cors import get_cors_headers

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
        print(
            f"### {self.event_counter}: ツール {tool.name} 終了. 結果: {result[:50]}.... 使用量: {self._usage_to_str(context.usage)}"
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

nutrition_agent = Agent(
    name="NutritionConversationalAgent",
    model="gpt-3.5-turbo",
    instructions="""
    """,
)

main_agent = Agent(
    name="MainAgent",
    model="gpt-3.5-turbo",
    instructions="""
    あなたはエージェントです。適当に会話してください。
    
    """,
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

    # メッセージ形式
    formatted_messages = [{"role": "user", "content": prompt}]
    
    try:
        # フックを指定してエージェントを実行
        result = asyncio.run(
            Runner.run(
                main_agent,
                formatted_messages,
                hooks=nutrition_hooks
            )
        )
        
        # エージェントの応答を取得
        agent_response = result.final_output
        
        return https_fn.Response(
            json.dumps({"message": agent_response}),
            status=200,
            headers=headers
        )
            
    except Exception as e:
        error_message = f"エージェント実行エラー: {str(e)}"
        
        # エラー時のフォールバック応答
        fallback_response = "申し訳ありません。処理中にエラーが発生しました。もう一度お試しください。"
        
        return https_fn.Response(
            json.dumps({"message": fallback_response, "error": str(e)}),
            status=500,
            headers=headers
        )
