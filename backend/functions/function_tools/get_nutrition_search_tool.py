from agents import function_tool
from typing import Any, Dict, List, Optional
from services.nutrition_search_service import NutritionSearchService

@function_tool(strict_mode=False)
def get_nutrition_search_tool(
    query: str,
    data_types: Optional[List[str]] = None,
    page_size: int = 25,
    page_number: int = 1
) -> Dict[str, Any]:
    """
    USDA FoodData Central の検索エンドポイント (/foods/search) を呼び出して、
    食材データ（fdcId、description、foodNutrients など）を取得します。

    Args:
        query: 検索クエリ (例: 食材名)
        data_types: API データタイプフィルタ (例: ['Foundation', 'Branded'])
        page_size: 取得件数 (最大200)
        page_number: ページ番号 (1-indexed)

    Returns:
        API レスポンスJSON または {"error": "..."}
    """
    service = NutritionSearchService()
    return service.search(query, data_types, page_size, page_number)