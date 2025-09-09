from agents import function_tool
from typing import Any, Dict
from services.nutrition_summary_service import NutritionSummaryService

@function_tool(strict_mode=False)
def calculate_nutrition_summary_tool(food_data: Dict[str, Any]) -> Dict[str, float]:
    """
    USDA FoodData Central 詳細APIのレスポンスを受け取り、
    主要栄養素を抜き出して辞書で返します。

    Args:
        food_data: get_nutrition_details_tool が返すJSON

    Returns:
        栄養サマリー辞書
    """
    service = NutritionSummaryService()
    return service.summarize(food_data)