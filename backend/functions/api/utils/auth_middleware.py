import firebase_admin
from firebase_admin import auth
from typing import Optional
from datetime import datetime, timedelta
from config import FIREBASE_ID_TOKEN_EXPIRY_MINUTES, FIREBASE_REFRESH_TOKEN_EXPIRY_DAYS

def create_custom_token_with_expiry(uid: str, additional_claims: dict = None) -> str:
    """
    設定された有効期限を持つカスタムトークンを作成
    
    Args:
        uid: Firebase UID
        additional_claims: 追加のクレーム
        
    Returns:
        custom_token: カスタムトークン
    """
    try:
        # 設定された分数後の有効期限を設定
        expires_at = datetime.utcnow() + timedelta(minutes=FIREBASE_ID_TOKEN_EXPIRY_MINUTES)
        
        claims = additional_claims or {}
        claims['exp'] = int(expires_at.timestamp())
        claims['refresh_token_expiry'] = int((datetime.utcnow() + timedelta(days=FIREBASE_REFRESH_TOKEN_EXPIRY_DAYS)).timestamp())
        
        custom_token = auth.create_custom_token(uid, claims)
        return custom_token.decode('utf-8')
    except Exception as e:
        print(f"❌ カスタムトークン作成失敗: {str(e)}")
        return None

def verify_firebase_token(id_token: str) -> Optional[str]:
    """
    Firebase IDトークンを検証し、user_idを返す
    
    Args:
        id_token: Firebase IDトークン
        
    Returns:
        user_id: 検証成功時のユーザーID、失敗時はNone
    """
    try:
        # Firebase Admin SDKでトークンを検証
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        
        # トークンの有効期限をチェック
        exp = decoded_token.get('exp', 0)
        current_time = datetime.utcnow().timestamp()
        
        if exp < current_time:
            print(f"❌ トークンが期限切れです")
            return None
            
        print(f"✅ 認証成功: user_id={user_id}, 有効期限: {FIREBASE_ID_TOKEN_EXPIRY_MINUTES}分")
        return user_id
    except Exception as e:
        print(f"❌ 認証失敗: {str(e)}")
        return None

def extract_user_id_from_request(request) -> Optional[str]:
    """
    リクエストから認証済みユーザーIDを取得
    
    Args:
        request: Flask/Firebase Functions リクエストオブジェクト
        
    Returns:
        user_id: 認証済みユーザーID、認証失敗時はNone
    """
    # Authorizationヘッダーからトークンを取得
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        print("❌ Authorizationヘッダーが見つかりません")
        return None
    
    # "Bearer "プレフィックスを除去
    if not auth_header.startswith('Bearer '):
        print("❌ 無効なAuthorizationヘッダー形式")
        return None
    
    id_token = auth_header[7:]  # "Bearer "を除去
    
    # トークンを検証してuser_idを取得
    return verify_firebase_token(id_token) 