"""
Firestore 上の users コレクションにレコードを 1 件作成するスクリプト
"""
import os
import sys

# スクリプト自身のディレクトリ
script_dir = os.path.dirname(os.path.abspath(__file__))
# プロジェクトルート
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
# backend/functions をモジュールとして読み込めるようパス追加
sys.path.append(project_root)

from firebase_admin import initialize_app
from repositories.users_repository import UsersRepository

# Firebase Admin SDK を初期化（credentials は環境変数で指定）
initialize_app()


def main():
    # サンプルデータ
    email = "a@gmail.com"
    password_hash = "password"
    name = "デモ　太朗"

    repo = UsersRepository()
    user_id = repo.create_user(email=email, password_hash=password_hash, name=name)
    print(f"ユーザーを作成しました: user_id={user_id}")


if __name__ == '__main__':
    main()
