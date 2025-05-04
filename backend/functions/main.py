from firebase_functions import https_fn
from firebase_admin import initialize_app
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Firebase Admin の初期化
initialize_app()

# 疎通確認用エンドポイント
@https_fn.on_request()
def helloWorld(request):
    return "Hello from Firebase Functions SDK for Python"

# 必要な API エンドポイントをインポートして登録
from api.agent import agent, agentsChat
from api.chat import saveChatMessage, getChatMessages
