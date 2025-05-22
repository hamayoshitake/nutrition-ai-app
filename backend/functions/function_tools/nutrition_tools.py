from agents import function_tool
from services.nutrition_service import NutritionService

@function_tool(strict_mode=False)
def save_nutrition_entry_tool(
    user_id: str,
    entry_date: str | None,
    meal_type: str | None,
    food_item: str | None,
    quantity_desc: str | None,
    nutrients: dict | None
) -> dict:
    """
    栄養エントリを保存します。型不一致・バリデーションエラーは success=False で返却します。
    """
    service = NutritionService()
    return service.save_entry(
        user_id,
        entry_date,
        meal_type,
        food_item,
        quantity_desc,
        nutrients
    )

@function_tool(strict_mode=False)
def get_nutrition_entry_tool(
    user_id: str,
    entry_id: str | None = None
) -> dict:
    """
    栄養エントリを取得するツール（サービス呼び出し版）
    """
    service = NutritionService()
    return service.get_entry(user_id, entry_id)
