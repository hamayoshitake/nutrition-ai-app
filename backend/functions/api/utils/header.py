import os

# 共通のHTTP関連関数
def get_cors_headers(request=None):
    ALLOWED_ORIGINS = {
        "http://localhost:3000",
        "https://v0-simple-chat-app-git-feature-581ad0-yoshitake-hamas-projects.vercel.app"
    }

    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        allow_origin = origin
    else:
        allow_origin = "null"
    print(f"🌐 Request origin: {origin}")

    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }
