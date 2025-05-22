from firebase_admin import firestore
from datetime import datetime
import uuid

class UsersRepository:
    def __init__(self):
        self.db = firestore.client()
        self.col = self.db.collection("users")

    def create_user(self, email: str, password_hash: str, name: str | None = None) -> str:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        data = {
            "id": user_id,
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "created_at": now,
            "updated_at": now,
        }
        self.col.document(user_id).set(data)
        return user_id

    def get_user_id_by_session(self, session_id: str) -> str | None:
        docs = (
            self.db
            .collection_group("chat_sessions")
            .where("id", "==", session_id)
            .limit(1)
            .get()
        )
        if not docs:
            return None
        # dict型に変換
        data = docs[0].to_dict()
        return data.get("user_id")