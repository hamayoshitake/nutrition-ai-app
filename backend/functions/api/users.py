# firestore_users_api.py
import json
from firebase_functions import https_fn
from repositories.users_repository import UsersRepository

# CORS設定

def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

@https_fn.on_request()
def createUser(request):
    headers = get_cors_headers()
    # OPTIONS プレフライト対応
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        if not email or not password:
            return https_fn.Response(
                json.dumps({"error": "email と password が必要です"}),
                status=400,
                headers=headers
            )
        repo = UsersRepository()
        user_id = repo.create_user(email=email, password_hash=password, name=name)
        return https_fn.Response(
            json.dumps({"id": user_id}),
            status=200,
            headers=headers
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers
        )
