# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

# from firebase_functions import https_fn
# from firebase_admin import initialize_app

# initialize_app()
#
#
# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello world!")

# main.py

# Cloud Functions for Firebase SDK をインポート
from firebase_functions import https_fn, firestore_fn

# Firebase Admin SDK をインポート
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import json

# .env ファイルを読み込む
load_dotenv()

# Firebase Admin 初期化
app = initialize_app()
db = firestore.client()

# OpenAI API キー設定
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# HTTP 関数 (REST API エンドポイント)
@https_fn.on_request()
def helloWorld(request):
    return "Hello from Firebase Functions SDK for Python"


# HTTP 関数：サンプルデータ追加
@https_fn.on_request()
def addSampleData(request):
    # リクエストボディ(JSON) を取得
    data = request.get_json(silent=True) or {"message": "sample", "timestamp": firestore.SERVER_TIMESTAMP}
    # Firestore に書き込み
    doc_ref = db.collection("samples").add(data)
    return {"id": doc_ref[1].id, **data}


# HTTP 関数：サンプルデータ取得
@https_fn.on_request()
def getSampleData(request):
    docs = db.collection("samples").get()
    items = [{"id": d.id, **d.to_dict()} for d in docs]
    return items


# HTTP 関数：AI エージェント呼び出し
@https_fn.on_request()
def agent(request):
    body = request.get_json(silent=True) or {}
    text = body.get("text")
    if not text:
        return {"error": "text フィールドが必要です"}, 400

    # ここで OpenAI Agents SDK を呼び出す
    from agents import Agent, Runner, trace

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


# HTTP 関数：Agents Chat test endpoint
@https_fn.on_request()
def agentsChat(request):
    # CORS と JSON Content-Type ヘッダー設定
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
    # プリフライト対応
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    # リクエスト JSON からプロンプトを取得
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt") or data.get("text")
    if not prompt:
        return https_fn.Response(json.dumps({"error": "prompt フィールドが必要です"}), status=400, headers=headers)

    # OpenAI Agent SDK があればそちらを利用
    try:
        from agents import Agent, Runner, trace
        agent_obj = Agent(
            name="chat-agent",
            instructions="ユーザーと会話を行ってください。"
        )
        with trace("chat-workflow"):
            result = Runner.run_sync(agent_obj, prompt)
        # Agent SDK レスポンスを JSON で返却
        return https_fn.Response(json.dumps({"message": result.final_output}), status=200, headers=headers)
    except Exception:
        # フォールバック: OpenAI API の ChatCompletion
        # OpenAI Python v1 SDK による ChatCompletion
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        message_text = resp.choices[0].message.content
        # Fallback レスポンスを JSON で返却
        return https_fn.Response(json.dumps({"message": message_text}), status=200, headers=headers)


# Firestore ドキュメント生成トリガー例
@firestore_fn.on_document_created(document="samples/{docId}")
def onSampleCreated(event):
    data = event.data.to_dict()
    print(f"新規サンプル作成: {event.data.id} → {data}")