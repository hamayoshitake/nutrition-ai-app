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

    def get_user_by_id(self, user_id: str) -> dict | None:
        doc = self.col.document(user_id).get()
        return doc.to_dict() if doc.exists else None

    def get_user_by_email(self, email: str) -> dict | None:
        qs = self.col.where("email", "==", email).limit(1).get()
        return qs[0].to_dict() if qs else None

    def update_user(self, user_id: str, **fields) -> bool:
        if not fields:
            return False
        fields["updated_at"] = datetime.utcnow().isoformat()
        doc_ref = self.col.document(user_id)
        if doc_ref.get().exists:
            doc_ref.update(fields)
            return True
        return False