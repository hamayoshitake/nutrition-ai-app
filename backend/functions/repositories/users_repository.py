from firebase_admin import firestore
from datetime import datetime

class UsersRepository:
    def __init__(self):
        self.db = firestore.client()
        self.col = self.db.collection("users")

    def create_user_profile(self, firebase_uid: str, email: str, name: str | None = None) -> bool:
        """Firebase AuthenticationのUIDを使ってFirestoreにユーザープロフィールを作成"""
        now = datetime.utcnow().isoformat()
        data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "name": name,
            "created_at": now,
            "updated_at": now,
        }
        # Firebase UIDをドキュメントIDとして使用
        self.col.document(firebase_uid).set(data)
        return True

    def get_user_profile(self, firebase_uid: str) -> dict | None:
        """Firebase UIDでユーザープロフィールを取得"""
        doc = self.col.document(firebase_uid).get()
        return doc.to_dict() if doc.exists else None

    def update_user_profile(self, firebase_uid: str, **fields) -> bool:
        """ユーザープロフィールを更新"""
        if not fields:
            return False
        
        fields["updated_at"] = datetime.utcnow().isoformat()
        doc_ref = self.col.document(firebase_uid)
        
        if doc_ref.get().exists:
            doc_ref.update(fields)
            return True
        return False

    def get_user_id_by_session(self, session_id: str) -> str | None:
        """セッションIDからFirebase UIDを取得"""
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