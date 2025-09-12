import os

# 共通のHTTP関連関数
def get_cors_headers(request=None):
    ALLOWED_ORIGINS = {
        "http://localhost:3000",
        "https://v0-simple-chat-app-gules.vercel.app",  # 現在のVercelメインURL
        "https://v0-simple-chat-app-git-feature-581ad0-yoshitake-hamas-projects.vercel.app"  # ブランチ用URL
    }

    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        allow_origin = origin
    else:
        allow_origin = "null"
    
    # 🔧 本番環境でのCORS詳細ログ追加
    print(f"🌐 Request origin: {origin}")
    print(f"🔍 CORS判定: 許可済み={origin in ALLOWED_ORIGINS}")
    print(f"📋 Allow-Origin設定: {allow_origin}")

    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }
