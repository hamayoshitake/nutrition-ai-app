"""栄養検索用ビジネスロジックを提供するサービスモジュール"""

import os
import requests
from typing import Any, Dict, List, Optional


class NutritionSearchService:
    """USDA FoodData Central の検索エンドポイントへの呼び出しを行うサービス"""
    def __init__(self):
        self.api_key = os.getenv("USDA_API_KEY")
        self.url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    def search(self, query: str, data_types: Optional[List[str]] = None, page_size: int = 25, page_number: int = 1) -> Dict[str, Any]:
        """食材検索を実行し、結果JSONを返却する"""
        api_key = os.getenv("USDA_API_KEY")
        if not api_key:
            return {"error": "USDA_API_KEY が設定されていません"}

        # api_keyはクエリパラメータとして送信
        url_with_key = f"{self.url}?api_key={api_key}"
        
        # JSONペイロードにはapi_keyを含めない
        payload: Dict[str, Any] = {"query": query, "pageSize": page_size, "pageNumber": page_number}
        if data_types:
            payload["dataType"] = data_types

        try:
            response = requests.post(url_with_key, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# このモジュール単体での動作確認
if __name__ == "__main__":
    from pprint import pprint
    service = NutritionSearchService()
    pprint(service.search("apple"))
