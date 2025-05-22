"""
栄養詳細取得用ビジネスロジックを提供するサービスモジュール
"""

import os
import requests
from typing import Any, Dict


class NutritionDetailsService:
    """
    USDA FoodData Central の詳細エンドポイントへの呼び出しを行うサービス
    """
    def __init__(self):
        self.base_url = "https://api.nal.usda.gov/fdc/v1/food"

    def get_details(self, fdc_id: int) -> Dict[str, Any]:
        """
        指定した fdcId の食材の詳細栄養情報を取得します。
        """
        api_key = os.getenv("USDA_API_KEY")
        if not api_key:
            return {"error": "USDA_API_KEY が設定されていません"}

        url = f"{self.base_url}/{fdc_id}"
        params = {"api_key": api_key}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)} 