"""
Firebase Functions メインエントリーポイント

主な仕様:
- 本番環境でエミュレータ設定を自動無効化
- Firebase Admin SDK の初期化
- API エンドポイントの登録

制限事項:
- 本番環境では FIRESTORE_EMULATOR_HOST 等を削除
"""

import os
from firebase_functions import https_fn
from firebase_admin import initialize_app

# 本番環境でエミュレータ設定を明示的に無効化
if os.getenv('FUNCTIONS_EMULATOR') is None:  # 本番環境の場合
    # エミュレータ関連の環境変数を削除
    emulator_vars = [
        'FIRESTORE_EMULATOR_HOST',
        'FIREBASE_AUTH_EMULATOR_HOST', 
        'FIREBASE_DATABASE_EMULATOR_HOST',
        'FIREBASE_STORAGE_EMULATOR_HOST',
        'PUBSUB_EMULATOR_HOST'
    ]
    
    for var in emulator_vars:
        if var in os.environ:
            print(f"🚫 本番環境でエミュレータ設定を削除: {var}={os.environ[var]}")
            del os.environ[var]
    
    print("✅ 本番環境: エミュレータ設定削除完了")
else:
    print("🔧 開発環境: エミュレータ設定を保持")

# Firebase Admin の初期化
initialize_app()

# 🔧 本番環境での環境変数確認ログ追加
print("🔍 Firebase Functions 起動時の環境変数確認:")
print(f"   📍 NODE_ENV: {os.getenv('NODE_ENV', '未設定')}")
print(f"   📍 FUNCTIONS_EMULATOR: {os.getenv('FUNCTIONS_EMULATOR', '未設定')}")
print(f"   📍 USDA_API_KEY: {'設定済み' if os.getenv('USDA_API_KEY') else '未設定'}")
print(f"   📍 FIRESTORE_EMULATOR_HOST: {os.getenv('FIRESTORE_EMULATOR_HOST', '未設定')}")

# 疎通確認用エンドポイント
@https_fn.on_request()
def helloWorld(request):
    return "Hello from Firebase Functions SDK for Python"

# 必要な API エンドポイントをインポートして登録
from api.agent import agent
from api.users import createUserProfile
