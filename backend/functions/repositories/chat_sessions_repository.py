from firebase_admin import firestore
from datetime import datetime
import uuid

class ChatSessionsRepository:
    def __init__(self):
        self.db = firestore.client()
        self.root = self.db.collection("users")

    def create_session(self, user_id: str) -> str:
        """
        新しいチャットセッションを作成し、セッションIDを返します。
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        data = {
            "id": session_id,
            "user_id": user_id,
            "started_at": now,
            "ended_at": None
        }
        # users/{user_id}/chat_sessions にドキュメントを作成
        self.root.document(user_id).collection("chat_sessions").document(session_id).set(data)
        return session_id

    def get_session(self, user_id: str, session_id: str) -> dict | None:
        """
        指定したセッションIDのチャットセッション情報を取得します。
        存在しない場合は None を返します。
        """
        # users/{user_id}/chat_sessions から指定セッションを取得
        doc = self.root.document(user_id).collection("chat_sessions").document(session_id).get()
        return doc.to_dict() if doc.exists else None

    def list_sessions(self, user_id: str) -> list[dict]:
        """
        指定ユーザーの全チャットセッションを開始日時順で取得します。
        """
        docs = (
            self.root
            .document(user_id)
            .collection("chat_sessions")
            .order_by("started_at")
            .get()
        )
        return [doc.to_dict() for doc in docs]

    def update_session(self, user_id: str, session_id: str, ended_at: str) -> bool:
        """
        指定ユーザーのチャットセッションの ended_at を更新します。
        """
        updates = {"ended_at": ended_at}
        doc_ref = self.root.document(user_id).collection("chat_sessions").document(session_id)
        if doc_ref.get().exists:
            doc_ref.update(updates)
            return True
        return False
