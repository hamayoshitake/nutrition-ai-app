#!/usr/bin/env python3
# test_nutrition_search_service.py

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import requests

# モジュール検索パスを設定 (backend/functions 直下)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.nutrition_search_service import NutritionSearchService

class TestNutritionSearchService:

    def setup_method(self):
        self.service = NutritionSearchService()

    def teardown_method(self):
        # 環境変数のクリア
        if "USDA_API_KEY" in os.environ:
            del os.environ["USDA_API_KEY"]

    def test_search_no_api_key(self):
        """環境変数が未設定の場合はエラーを返す"""
        if "USDA_API_KEY" in os.environ:
            del os.environ["USDA_API_KEY"]
        result = self.service.search("apple")
        assert "error" in result
        assert "設定されていません" in result["error"]

    def test_search_success(self, monkeypatch):
        """正常系: API呼び出しが成功する場合"""
        monkeypatch.setenv("USDA_API_KEY", "dummy-key")
        dummy_response = MagicMock()
        dummy_response.raise_for_status.return_value = None
        dummy_response.json.return_value = {"foods": [{"id": 1}]}  

        with patch("services.nutrition_search_service.requests.post", return_value=dummy_response) as mock_post:
            result = self.service.search("apple", ["Foundation"], 5, 2)
            mock_post.assert_called_once_with(
                self.service.url,
                json={
                    "api_key": "dummy-key",
                    "query": "apple",
                    "pageSize": 5,
                    "pageNumber": 2,
                    "dataType": ["Foundation"]
                }
            )
            assert result == {"foods": [{"id": 1}]}  

    def test_search_http_error(self, monkeypatch):
        """異常系: HTTPエラー発生時はエラーを返す"""
        monkeypatch.setenv("USDA_API_KEY", "dummy-key")
        dummy_response = MagicMock()
        dummy_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

        with patch("services.nutrition_search_service.requests.post", return_value=dummy_response):
            result = self.service.search("apple")
            assert "error" in result
            assert "404 Not Found" in result["error"]

    def test_search_exception(self, monkeypatch):
        """異常系: その他例外発生時はエラーを返す"""
        monkeypatch.setenv("USDA_API_KEY", "dummy-key")
        with patch("services.nutrition_search_service.requests.post", side_effect=Exception("conn err")):
            result = self.service.search("apple")
            assert "error" in result
            assert "conn err" in result["error"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 