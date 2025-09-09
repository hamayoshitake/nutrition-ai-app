#!/usr/bin/env python3
# test_nutrition_service.py
# NutritionService クラスのテスト

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# backend/functions 直下をモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.nutrition_service import NutritionService
from repositories.nutrition_entries_repository import NutritionEntriesRepository

class TestNutritionService:

    def setup_method(self):
        # テスト用パラメータ
        self.user_id = "user_1"
        self.entry_date = "2025-05-22"
        self.meal_type = "breakfast"
        self.food_item = "apple"
        self.quantity_desc = "100g"
        self.nutrients = {"calories": 52}

        # リポジトリをモック化
        self.mock_repo = MagicMock(spec=NutritionEntriesRepository)
        self.patcher = patch('services.nutrition_service.NutritionEntriesRepository', return_value=self.mock_repo)
        self.patcher.start()

        # サービスインスタンス
        self.service = NutritionService()

    def teardown_method(self):
        self.patcher.stop()

    def test_save_entry_success(self):
        # 正常系: リポジトリがUUID文字列を返す
        self.mock_repo.create_entry.return_value = "entry-uuid-123"
        result = self.service.save_entry(
            self.user_id,
            self.entry_date,
            self.meal_type,
            self.food_item,
            self.quantity_desc,
            self.nutrients
        )
        # リポジトリ呼び出し検証
        self.mock_repo.create_entry.assert_called_once_with(
            self.user_id,
            self.entry_date,
            self.meal_type,
            self.food_item,
            self.quantity_desc,
            self.nutrients
        )
        # 戻り値検証
        assert result["success"] is True
        assert result["entry_id"] == "entry-uuid-123"

    def test_save_entry_invalid_params(self):
        # 異常系: パラメータ型エラー
        result = self.service.save_entry(
            user_id=123,
            entry_date=None,
            meal_type=self.meal_type,
            food_item=self.food_item,
            quantity_desc=self.quantity_desc,
            nutrients=self.nutrients
        )
        assert result["success"] is False
        assert "パラメータが不正" in result["error"]

    def test_save_entry_exception(self):
        # 異常系: リポジトリ側で例外
        self.mock_repo.create_entry.side_effect = Exception("DB接続失敗")
        result = self.service.save_entry(
            self.user_id,
            self.entry_date,
            self.meal_type,
            self.food_item,
            self.quantity_desc,
            self.nutrients
        )
        assert result["success"] is False
        assert "サーバーエラー" in result["error"]
        assert "DB接続失敗" in result["error"]

    # get_entryメソッドのテストを追加
    def test_get_entry_success(self):
        """正常系: エントリが存在する場合のテスト"""
        entry_data = {"id": "entry1", "user_id": self.user_id, "field": "value"}
        self.mock_repo.get_entry.return_value = entry_data
        result = self.service.get_entry(self.user_id, "entry1")
        self.mock_repo.get_entry.assert_called_once_with(self.user_id, "entry1")
        assert result["success"] is True
        assert result["entry"] == entry_data

    def test_get_entry_not_found(self):
        """異常系: エントリが見つからない場合のテスト"""
        self.mock_repo.get_entry.return_value = None
        result = self.service.get_entry(self.user_id, "missing")
        self.mock_repo.get_entry.assert_called_once_with(self.user_id, "missing")
        assert result["success"] is False
        assert "エントリが見つかりません" in result.get("error", "")

    def test_get_entry_invalid_params(self):
        """異常系: 無効なパラメータの場合のテスト"""
        result = self.service.get_entry(self.user_id, None)
        assert result["success"] is False
        assert "無効な user_id または entry_id です" in result.get("error", "")

    def test_get_entry_exception(self):
        """異常系: リポジトリ側で例外が発生した場合のテスト"""
        self.mock_repo.get_entry.side_effect = Exception("DB読取失敗")
        result = self.service.get_entry(self.user_id, "entry1")
        assert result["success"] is False
        assert "サーバーエラー" in result.get("error", "")
        assert "DB読取失敗" in result.get("error", "")

    # 新しいメソッドのテスト
    def test_get_entries_by_date_success(self):
        """正常系: 日付ベースでエントリを取得する場合のテスト"""
        entries_data = [
            {"id": "entry1", "user_id": self.user_id, "entry_date": "2025-05-26", "food_item": "rice"},
            {"id": "entry2", "user_id": self.user_id, "entry_date": "2025-05-26", "food_item": "chicken"}
        ]
        self.mock_repo.get_entries_by_date.return_value = entries_data
        result = self.service.get_entries_by_date(self.user_id, "2025-05-26")
        
        self.mock_repo.get_entries_by_date.assert_called_once_with(self.user_id, "2025-05-26")
        assert result["success"] is True
        assert result["entries"] == entries_data
        assert result["entry_date"] == "2025-05-26"
        assert result["count"] == 2

    def test_get_entries_by_date_no_date(self):
        """正常系: 日付を指定しない場合のテスト（今日の日付を使用）"""
        entries_data = []
        self.mock_repo.get_entries_by_date.return_value = entries_data
        
        # datetime_utilsのインポートをモック化
        with patch('services.nutrition_service.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-05-26"
            result = self.service.get_entries_by_date(self.user_id, None)
        
        # 今日の日付で呼び出されることを確認
        self.mock_repo.get_entries_by_date.assert_called_once_with(self.user_id, "2025-05-26")
        assert result["success"] is True
        assert result["entries"] == entries_data
        assert result["count"] == 0

    def test_get_entries_by_date_invalid_user_id(self):
        """異常系: 無効なuser_idの場合のテスト"""
        result = self.service.get_entries_by_date("", "2025-05-26")
        assert result["success"] is False
        assert "無効な user_id です" in result.get("error", "")

    def test_get_entries_by_date_exception(self):
        """異常系: リポジトリ側で例外が発生した場合のテスト"""
        self.mock_repo.get_entries_by_date.side_effect = Exception("DB読取失敗")
        result = self.service.get_entries_by_date(self.user_id, "2025-05-26")
        assert result["success"] is False
        assert "サーバーエラー" in result.get("error", "")
        assert "DB読取失敗" in result.get("error", "")

    def test_get_all_entries_success(self):
        """正常系: 全エントリを取得する場合のテスト"""
        entries_data = [
            {"id": "entry1", "user_id": self.user_id, "created_at": "2025-05-26T10:00:00"},
            {"id": "entry2", "user_id": self.user_id, "created_at": "2025-05-25T10:00:00"}
        ]
        self.mock_repo.get_all_entries.return_value = entries_data
        result = self.service.get_all_entries(self.user_id, 100)
        
        self.mock_repo.get_all_entries.assert_called_once_with(self.user_id, 100)
        assert result["success"] is True
        assert result["entries"] == entries_data
        assert result["count"] == 2

    def test_get_all_entries_invalid_user_id(self):
        """異常系: 無効なuser_idの場合のテスト"""
        result = self.service.get_all_entries("", 50)
        assert result["success"] is False
        assert "無効な user_id です" in result.get("error", "")

    def test_get_all_entries_exception(self):
        """異常系: リポジトリ側で例外が発生した場合のテスト"""
        self.mock_repo.get_all_entries.side_effect = Exception("DB読取失敗")
        result = self.service.get_all_entries(self.user_id, 50)
        assert result["success"] is False
        assert "サーバーエラー" in result.get("error", "")
        assert "DB読取失敗" in result.get("error", "")

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])