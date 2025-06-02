# firestore_users_api.py
import json
from firebase_functions import https_fn
from repositories.users_repository import UsersRepository
from .utils.auth_middleware import extract_user_id_from_request

# CORS設定

def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }

@https_fn.on_request()
def createUserProfile(request):
    """Firebase Authenticationと連携するユーザープロフィール作成API"""
    headers = get_cors_headers()
    # OPTIONS プレフライト対応
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=headers)

    # 認証済みuser_idを取得
    firebase_uid = extract_user_id_from_request(request)
    if not firebase_uid:
        return https_fn.Response(
            json.dumps({"error": "認証が必要です"}),
            status=401,
            headers=headers
        )

    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        name = data.get("name")
        
        if not email:
            return https_fn.Response(
                json.dumps({"error": "email が必要です"}),
                status=400,
                headers=headers
            )
        
        repo = UsersRepository()
        success = repo.create_user_profile(firebase_uid=firebase_uid, email=email, name=name)
        
        if success:
            return https_fn.Response(
                    json.dumps({"success": True, "firebase_uid": firebase_uid}),
                status=200,
                headers=headers
            )
        else:
            return https_fn.Response(
                json.dumps({"error": "ユーザープロフィール作成に失敗しました"}),
                status=500,
                headers=headers
            )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers
        )
