"""
栄養エントリに関するビジネスロジックを提供するサービスモジュール
"""

from repositories.nutrition_entries_repository import NutritionEntriesRepository
from datetime import datetime


class NutritionService:
    """
    栄養エントリの保存機能を提供するサービスクラス
    """

    def __init__(self):
        self.repo = NutritionEntriesRepository()

    def save_entry(
        self,
        user_id: str,
        entry_date: str,
        meal_type: str,
        food_item: str,
        quantity_desc: str,
        nutrients: dict
    ) -> dict:
        """
        栄養エントリを保存します。型検証と例外処理を行い、結果を辞書で返却します。
        """
        # パラメータの型チェック
        if not (
            isinstance(user_id, str)
            and isinstance(entry_date, str)
            and isinstance(meal_type, str)
            and isinstance(food_item, str)
            and isinstance(quantity_desc, str)
            and isinstance(nutrients, dict)
        ):
            return {"success": False, "error": "ツールのパラメータが不正です"}

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

    def get_entries_by_date(self, user_id: str, entry_date: str | None = None) -> dict:
        """
        指定した日付の栄養エントリを全て取得します。
        
        Args:
            user_id: ユーザーID
            entry_date: 取得したい日付（YYYY-MM-DD形式）。指定しない場合は今日の日付
            
        Returns:
            該当する栄養エントリのリスト
        """
        # パラメータの型チェック
        if not isinstance(user_id, str) or not user_id.strip():
            return {"success": False, "error": "無効な user_id です"}
        
        # entry_dateが指定されていない場合は今日の日付を使用
        if entry_date is None:
            entry_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            entries = self.repo.get_entries_by_date(user_id, entry_date)
            return {
                "success": True, 
                "entries": entries, 
                "entry_date": entry_date,
                "count": len(entries)
            }
        except Exception as e:
            return {"success": False, "error": "サーバーエラー: " + str(e)}

    def get_all_entries(self, user_id: str, limit: int = 50) -> dict:
        """
        ユーザーの全栄養エントリを取得します（最新順）。
        
        Args:
            user_id: ユーザーID
            limit: 取得件数の上限
            
        Returns:
            栄養エントリのリスト
        """
        # パラメータの型チェック
        if not isinstance(user_id, str) or not user_id.strip():
            return {"success": False, "error": "無効な user_id です"}
        
        try:
            entries = self.repo.get_all_entries(user_id, limit)
            return {
                "success": True, 
                "entries": entries, 
                "count": len(entries)
            }
        except Exception as e:
            return {"success": False, "error": "サーバーエラー: " + str(e)} 