from firebase_admin import firestore
from datetime import datetime
import uuid

class ChatsRepository:
    def __init__(self):
        self.db = firestore.client()
        self.root = self.db.collection("users")

    def create_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        message_text: str,
        parent_message_id: str | None = None
    ) -> bool:
        """
        指定ユーザーのチャットセッション下にチャットメッセージを保存します。
        """
        now = datetime.utcnow().isoformat()
        data = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "parent_message_id": parent_message_id,
            "user_id": user_id,
            "role": role,
            "message_text": message_text,
            "created_at": now
        }
        doc_ref = (
            self.root
            .document(user_id)
            .collection("chat_sessions")
            .document(session_id)
            .collection("chat_messages")
            .document(data["id"])
        )
        doc_ref.set(data)
        return True

    def get_messages(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        """
        指定ユーザーのチャットセッションからメッセージ一覧を取得します。
        """
        query = (
            self.root
            .document(user_id)
            .collection("chat_sessions")
            .document(session_id)
            .collection("chat_messages")
            .order_by("created_at")
            .offset(offset)
            .limit(limit)
            .get()
        )
        messages = []
        for doc in query:
            msg = doc.to_dict()
            msg["doc_id"] = doc.id
            messages.append(msg)
        return messages
