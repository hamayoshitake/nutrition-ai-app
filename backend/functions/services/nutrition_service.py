"""
栄養エントリに関するビジネスロジックを提供するサービスモジュール
"""

from repositories.nutrition_entries_repository import NutritionEntriesRepository


class NutritionService:
    """
    栄養エントリの保存機能を提供するサービスクラス
    """

    def __init__(self):
        self.repo = NutritionEntriesRepository()

    def save_entry(
        self,
        user_id: str,
        entry_date: str | None,
        meal_type: str | None,
        food_item: str | None,
        quantity_desc: str | None,
        nutrients: dict | None
    ) -> dict:
        """
        栄養エントリを保存します。型検証と例外処理を行い、結果を辞書で返却します。
        """
        # 必須パラメータのチェック
        if not isinstance(user_id, str) or not user_id.strip():
            return {"success": False, "error": "user_idが不正です"}
        
        # デフォルト値の設定
        if entry_date is None:
            from datetime import datetime
            entry_date = datetime.now().strftime("%Y-%m-%d")
        
        if meal_type is None:
            meal_type = "その他"
        
        if food_item is None:
            return {"success": False, "error": "food_itemは必須です"}
        
        if quantity_desc is None:
            quantity_desc = "適量"
        
        if nutrients is None:
            nutrients = {}
        
        # パラメータの型チェック（デフォルト値設定後）
        if not (
            isinstance(user_id, str)
            and isinstance(entry_date, str)
            and isinstance(meal_type, str)
            and isinstance(food_item, str)
            and isinstance(quantity_desc, str)
            and isinstance(nutrients, dict)
        ):
            return {"success": False, "error": "ツールのパラメータの型が不正です"}

        try:
            entry_id = self.repo.create_entry(
                user_id, entry_date, meal_type, food_item, quantity_desc, nutrients
            )
            return {"success": True, "entry_id": entry_id}
        except ValueError as ve:
            return {"success": False, "error": str(ve)}
        except Exception as e:
            return {"success": False, "error": "サーバーエラー: " + str(e)}

    def get_entry(self, user_id: str, entry_id: str) -> dict:
        """
        栄養エントリを取得します。型検証と例外処理を行い、結果を辞書で返却します。
        """
        # パラメータの型チェック
        if not (
            isinstance(user_id, str)
            and isinstance(entry_id, str)
        ):
            return {"success": False, "error": "無効な user_id または entry_id です"}

        try:
            entry = self.repo.get_entry(user_id, entry_id)
            if entry is None:
                return {"success": False, "error": "エントリが見つかりません"}
            return {"success": True, "entry": entry}
        except Exception as e:
            return {"success": False, "error": "サーバーエラー: " + str(e)} 