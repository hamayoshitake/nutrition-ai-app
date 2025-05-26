from firebase_admin import firestore
from datetime import datetime
import uuid

class NutritionEntriesRepository:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.root = self.db.collection("users")

    def create_entry(
        self,
        user_id: str,
        entry_date: str,
        meal_type: str,
        food_item: str,
        quantity_desc: str,
        nutrients: dict
    ) -> str:
        """
        新しい栄養エントリを作成し、entry_id を返します。
        """
        entry_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        data = {
            "id": entry_id,
            "user_id": user_id,
            "entry_date": entry_date,
            "meal_type": meal_type,
            "food_item": food_item,
            "quantity_desc": quantity_desc,
            "nutrients": nutrients,
            "created_at": now
        }
        # users/{user_id}/nutrition_entries/{entry_id} にドキュメントを作成
        self.root.document(user_id).collection("nutrition_entries").document(entry_id).set(data)
        return entry_id

    def get_entry(self, user_id: str, entry_id: str) -> dict | None:
        """
        指定した栄養エントリを取得します。
        """
        doc = (
            self.root
            .document(user_id)
            .collection("nutrition_entries")
            .document(entry_id)
            .get()
        )
        return doc.to_dict() if doc.exists else None

    def update_entry(self, user_id: str, entry_id: str, **fields) -> bool:
        """
        指定した栄養エントリを更新します。
        fields に entry_date, meal_type, food_item, quantity_desc, nutrients を指定可能です。
        """
        if not fields:
            return False
        doc_ref = (
            self.root
            .document(user_id)
            .collection("nutrition_entries")
            .document(entry_id)
        )
        if doc_ref.get().exists:
            doc_ref.update(fields)
            return True
        return False

    def get_entries_by_date(self, user_id: str, entry_date: str) -> list[dict]:
        """
        指定した日付の栄養エントリを全て取得します。
        
        Args:
            user_id: ユーザーID
            entry_date: 取得したい日付（YYYY-MM-DD形式）
            
        Returns:
            該当する栄養エントリのリスト
        """
        try:
            docs = (
                self.root
                .document(user_id)
                .collection("nutrition_entries")
                .where("entry_date", "==", entry_date)
                .stream()
            )
            return [doc.to_dict() for doc in docs if doc.exists]
        except Exception:
            return []

    def get_all_entries(self, user_id: str, limit: int = 100) -> list[dict]:
        """
        ユーザーの全栄養エントリを取得します（最新順）。
        
        Args:
            user_id: ユーザーID
            limit: 取得件数の上限
            
        Returns:
            栄養エントリのリスト
        """
        try:
            docs = (
                self.root
                .document(user_id)
                .collection("nutrition_entries")
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            return [doc.to_dict() for doc in docs if doc.exists]
        except Exception:
            return []
