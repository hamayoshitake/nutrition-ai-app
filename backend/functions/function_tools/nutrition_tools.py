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

@function_tool(strict_mode=False)
def get_nutrition_entries_by_date_tool(
    user_id: str,
    entry_date: str | None = None
) -> dict:
    """
    指定した日付の栄養エントリを全て取得するツール
    
    Args:
        user_id: ユーザーID
        entry_date: 取得したい日付（YYYY-MM-DD形式）。指定しない場合は今日の日付
    
    Returns:
        該当する栄養エントリのリスト
    """
    service = NutritionService()
    return service.get_entries_by_date(user_id, entry_date)

@function_tool(strict_mode=False)
def get_all_nutrition_entries_tool(
    user_id: str,
    limit: int = 50
) -> dict:
    """
    ユーザーの全栄養エントリを取得するツール（最新順）
    
    Args:
        user_id: ユーザーID
        limit: 取得件数の上限
    
    Returns:
        栄養エントリのリスト
    """
    service = NutritionService()
    return service.get_all_entries(user_id, limit)
