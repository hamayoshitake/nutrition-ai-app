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
        
        # 🔧 API key の状態をログ出力（本番環境での確認用）
        print(f"🔑 USDA API Key 確認（詳細取得）: 設定済み={api_key is not None}, 長さ={len(api_key) if api_key else 0}, 先頭4文字={api_key[:4] if api_key else 'なし'}")
        
        if not api_key:
            print("❌ USDA_API_KEY が設定されていません - 環境変数を確認してください")
            return {"error": "USDA_API_KEY が設定されていません"}

        url = f"{self.base_url}/{fdc_id}"
        params = {"api_key": api_key}

        try:
            print(f"🌐 USDA API詳細取得リクエスト送信: fdcId={fdc_id}, URL={url}")
            response = requests.get(url, params=params)
            print(f"✅ USDA API詳細取得レスポンス: ステータス={response.status_code}")
            response.raise_for_status()
            result = response.json()
            food_name = result.get('description', '不明')
            print(f"🍽️ USDA API詳細取得成功: {food_name} (fdcId: {fdc_id})")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ USDA API詳細取得エラー: {str(e)}")
            return {"error": f"USDA API詳細取得エラー: {str(e)}"}
        except Exception as e:
            print(f"❌ 予期しないエラー（詳細取得）: {str(e)}")
            return {"error": f"予期しないエラー: {str(e)}"} 