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
        
        # 🔧 API key の状態をログ出力（本番環境での確認用）
        print(f"🔑 USDA API Key 確認: 設定済み={api_key is not None}, 長さ={len(api_key) if api_key else 0}, 先頭4文字={api_key[:4] if api_key else 'なし'}")
        
        if not api_key:
            print("❌ USDA_API_KEY が設定されていません - 環境変数を確認してください")
            return {"error": "USDA_API_KEY が設定されていません"}

        # api_keyはクエリパラメータとして送信
        url_with_key = f"{self.url}?api_key={api_key}"
        
        # JSONペイロードにはapi_keyを含めない
        payload: Dict[str, Any] = {"query": query, "pageSize": page_size, "pageNumber": page_number}
        if data_types:
            payload["dataType"] = data_types

        try:
            print(f"🌐 USDA API検索リクエスト送信: query={query}, URL={self.url}")
            response = requests.post(url_with_key, json=payload)
            print(f"✅ USDA API検索レスポンス: ステータス={response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"📊 USDA API検索結果: {len(result.get('foods', []))}件の食品が見つかりました")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ USDA API検索エラー: {str(e)}")
            return {"error": f"USDA API検索エラー: {str(e)}"}
        except Exception as e:
            print(f"❌ 予期しないエラー（検索）: {str(e)}")
            return {"error": f"予期しないエラー: {str(e)}"}

# このモジュール単体での動作確認
if __name__ == "__main__":
    from pprint import pprint
    service = NutritionSearchService()
    pprint(service.search("apple"))
