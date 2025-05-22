#!/usr/bin/env python3
# test_nutrition_details_service.py

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import requests

# backend/functions 直下をモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.nutrition_details_service import NutritionDetailsService

class TestNutritionDetailsService:

    def setup_method(self):
        self.service = NutritionDetailsService()

    def teardown_method(self):
        if "USDA_API_KEY" in os.environ:
            del os.environ["USDA_API_KEY"]

    def test_get_details_no_api_key(self):
        """環境変数が未設定の場合はエラーを返す"""
        if "USDA_API_KEY" in os.environ:
            del os.environ["USDA_API_KEY"]
        result = self.service.get_details(12345)
        assert "error" in result
        assert "設定されていません" in result["error"]

    def test_get_details_success(self, monkeypatch):
        """正常系: API呼び出しが成功する場合"""
        monkeypatch.setenv("USDA_API_KEY", "dummy-key")
        dummy_response = MagicMock()
        dummy_response.raise_for_status.return_value = None
        dummy_response.json.return_value = {"description": "Apple", "id": 12345}

        with patch("services.nutrition_details_service.requests.get", return_value=dummy_response) as mock_get:
            result = self.service.get_details(12345)
            mock_get.assert_called_once_with(
                f"https://api.nal.usda.gov/fdc/v1/food/12345",
                params={"api_key": "dummy-key"}
            )
            assert result == {"description": "Apple", "id": 12345}

    def test_get_details_http_error(self, monkeypatch):
        """異常系: HTTPエラー発生時はエラーを返す"""
        monkeypatch.setenv("USDA_API_KEY", "dummy-key")
        dummy_response = MagicMock()
        dummy_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

        with patch("services.nutrition_details_service.requests.get", return_value=dummy_response):
            result = self.service.get_details(12345)
            assert "error" in result
            assert "404 Not Found" in result["error"]

    def test_get_details_exception(self, monkeypatch):
        """異常系: その他例外発生時はエラーを返す"""
        monkeypatch.setenv("USDA_API_KEY", "dummy-key")
        with patch("services.nutrition_details_service.requests.get", side_effect=Exception("conn err")):
            result = self.service.get_details(12345)
            assert "error" in result
            assert "conn err" in result["error"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 