from agents import function_tool
from typing import Any, Dict
from services.nutrition_details_service import NutritionDetailsService

@function_tool(strict_mode=False)
def get_nutrition_details_tool(fdc_id: int) -> Dict[str, Any]:
    """
    USDA FoodData Central の詳細エンドポイント (/v1/food/{fdcId}) から、
    指定した fdcId の食材の詳細栄養情報を取得します。

    Args:
        fdc_id (int): 検索結果から取得した fdcId

    Returns:
        Dict[str, Any]: APIレスポンスのJSONデータ または {"error": "..."}
    """
    service = NutritionDetailsService()
    return service.get_details(fdc_id)