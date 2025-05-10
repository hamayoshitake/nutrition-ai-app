from firebase_functions import https_fn
from firebase_admin import initialize_app

# Firebase Admin の初期化
initialize_app()

# 疎通確認用エンドポイント
@https_fn.on_request()
def helloWorld(request):
    return "Hello from Firebase Functions SDK for Python"

# 必要な API エンドポイントをインポートして登録
from api.agent import agent
from api.users import createUser
