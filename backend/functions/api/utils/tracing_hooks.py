"""
栄養AIアプリ用の詳細トレーシングフック
"""

from agents import RunHooks, RunContextWrapper, Usage, Tool, Agent
from datetime import datetime
from typing import Any, Dict, List


class DetailedNutritionHooks(RunHooks):
    """
    栄養AIアプリ用の詳細トレーシングフック
    エージェントの実行状況、ツール呼び出し、LLM生成、エラーを詳細に記録します
    """

    def __init__(self):
        self.event_counter = 0
        self.tool_calls = []
        self.llm_generations = []
        self.errors = []

    def _usage_to_str(self, usage: Usage) -> str:
        """使用量情報を文字列に変換"""
        return f"{usage.requests} requests, {usage.input_tokens} input tokens, {usage.output_tokens} output tokens, {usage.total_tokens} total tokens"

    def _log_with_timestamp(self, message: str) -> None:
        """タイムスタンプ付きでログを出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """エージェント開始時の処理"""
        self.event_counter += 1
        self._log_with_timestamp(
            f"🚀 ### {self.event_counter}: エージェント {agent.name} 開始"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")
        self._log_with_timestamp(f"🔧 利用可能ツール: {[tool.name for tool in agent.tools]}")

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        """エージェント終了時の処理"""
        self.event_counter += 1
        self._log_with_timestamp(
            f"🏁 ### {self.event_counter}: エージェント {agent.name} 終了"
        )
        self._log_with_timestamp(f"📊 最終使用量: {self._usage_to_str(context.usage)}")
        self._log_with_timestamp(f"📝 最終出力: {str(output)[:200]}...")

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        """ツール開始時の処理"""
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
        """ツール終了時の処理"""
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
        """LLM生成開始時の処理"""
        self.event_counter += 1
        self._log_with_timestamp(
            f"🧠 ### {self.event_counter}: LLM生成開始 (エージェント: {agent.name})"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")

    async def on_generation_end(self, context: RunContextWrapper, agent: Agent, output: str) -> None:
        """LLM生成終了時の処理"""
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
        """エージェント間のハンドオフ時の処理"""
        self.event_counter += 1
        self._log_with_timestamp(
            f"🔄 ### {self.event_counter}: {from_agent.name} から {to_agent.name} へハンドオフ"
        )
        self._log_with_timestamp(f"📊 使用量: {self._usage_to_str(context.usage)}")

    async def on_error(self, context: RunContextWrapper, error: Exception) -> None:
        """エラー発生時の処理"""
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
        if any(phrase in prompt_lower for phrase in ["今日の栄養", "栄養記録", "摂取量", "栄養状況", "栄養摂取状況"]):
            analysis["expected_tools"].append("get_nutrition_entries_by_date_tool")
            if analysis["prompt_type"] == "unknown":
                analysis["prompt_type"] = "nutrition_status"
        
        analysis["keywords"] = list(set(found_keywords))
        analysis["expected_tools"] = list(set(analysis["expected_tools"]))  # 重複除去
        
        return analysis

    def reset(self) -> None:
        """フック状態をリセット（新しいリクエスト用）"""
        self.event_counter = 0
        self.tool_calls = []
        self.llm_generations = []
        self.errors = [] 