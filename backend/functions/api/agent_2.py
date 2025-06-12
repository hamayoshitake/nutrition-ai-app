import json
import asyncio
from firebase_functions import https_fn
from agents import Agent, Runner, trace
from function_tools.chat_tools import create_chat_message_tool, get_chat_messages_tool

from .utils.cors import get_cors_headers

def check_session_cookie(request):
    session_id = request.cookies.get("session_id")
    is_new_session = False
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        is_new_session = True
    return session_id, is_new_session

# nutrition_agent = Agent(
#     name="nutrition_agent",
#     instructions="Handoff to the appropriate agent based on the language of the request.",
#     tools=[create_chat_message_tool, get_chat_messages_tool],
# )

# nutrition_agent = Agent(
#     name="NutritionAgent",
#     tools=[create_chat_message_tool, get_chat_messages_tool],
#     llm="gpt-4o",
#     instructions="""
#       あなたは栄養計算エージェントです。
#       入力 items と meal_type、userContext を受け取り：
#         1) チャット履歴の保存
#         2) 決定論的ロジックで nutrients を計算
#         3) firestore_add("nutrition_entries", {...}) で保存
#         4) 計算結果を JSON で返してください。
#       """
# )
nutrition_agent = Agent(
    name="NutritionAgent",
    tools=[create_chat_message_tool, get_chat_messages_tool],
    model="gpt‑4o",
    instructions="""
      あなたは栄養計算エージェントです。
      入力 items と meal_type、userContext を受け取り：
        1) チャット履歴の保存
        2) 決定論的ロジックで nutrients を計算
        3) 計算結果を JSON で返してください。
      """
)

@https_fn.on_request()
def agent(request):
    headers = get_cors_headers()
    session_id, is_new_session = check_session_cookie(request)
    body = request.get_json(silent=True) or {}
    text = body.get("prompt")
    if not text:
        return {"error": "prompt フィールドが必要です"}, 400
    with trace("nutrition-workflow"):
        result = asyncio.run(Runner.run(nutrition_agent, text))
    return https_fn.Response(json.dumps({"message": result.final_output}), status=200, headers=headers)
