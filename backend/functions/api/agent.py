from firebase_functions import https_fn
import json
from agents import Agent, Runner, trace
import asyncio

@https_fn.on_request()
def agent(request):
    body = request.get_json(silent=True) or {}
    text = body.get("text")
    if not text:
        return {"error": "text フィールドが必要です"}, 400
    agent_obj = Agent(
        name="nutrition-agent",
        instructions=(
            "ユーザーのフリーテキストから栄養素を推論して計算してください。"
            "必要に応じて追加情報を質問してください。"
        )
    )
    with trace("nutrition-workflow"):
        result = Runner.run_sync(agent_obj, text)
    return {"type": "ai_response", "message": result.final_output}

@https_fn.on_request()
def agentsChat(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    # Cookieによるユーザーセッション管理
    session_id = request.cookies.get("session_id")
    new_session = False
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        new_session = True

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt") or data.get("text")
    if not prompt:
        return https_fn.Response(json.dumps({"error": "prompt フィールドが必要です"}), status=400, headers=headers)
    try:
        agent = Agent(
            name="Math Tutor",
            instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
        )
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        result = loop.run_until_complete(Runner.run(agent, prompt))
        print(result.final_output)
        print("agentsChat: executed Agent SDK branch")

        # Chat履歴の保存
        from repositories.chat_repository import ChatService
        chat_service = ChatService()
        chat_service.save_message(session_id, session_id, "user", prompt)
        chat_service.save_message(session_id, session_id, "agent", result.final_output)

        if new_session:
            headers["Set-Cookie"] = f"session_id={session_id}; Path=/; HttpOnly"

        return https_fn.Response(json.dumps({"message": result.final_output, "session_id": session_id}), status=200, headers=headers)
    except Exception as e:
        print(f"agentsChat: Agent SDK error: {e}")
        return https_fn.Response(json.dumps({"error": "エージェント呼び出しに失敗しました"}), status=500, headers=headers)