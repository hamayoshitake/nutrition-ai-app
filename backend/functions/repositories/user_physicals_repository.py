from firebase_admin import firestore
from datetime import datetime

class UserPhysicalsRepository:
    def __init__(self):
        self.db = firestore.client()
        self.root = self.db.collection("users")

    def upsert_physical(
        self,
        user_id: str,
        weight: float | None = None,
        height: float | None = None,
        body_fat: float | None = None,
        age: int | None = None,
        gender: str | None = None,
    ) -> bool:
        doc_ref = self.root.document(user_id).collection("physical").document("profile")
        now = datetime.utcnow().isoformat()
        data = {"updated_at": now}
        for k, v in (("weight", weight), ("height", height), ("body_fat", body_fat), ("age", age), ("gender", gender)):
            if v is not None:
                data[k] = v
        doc_ref.set(data, merge=True)
        return True

    def get_physical_by_user(self, user_id: str) -> dict | None:
        doc = self.root.document(user_id).collection("physical").document("profile").get()
        return doc.to_dict() if doc.exists else None