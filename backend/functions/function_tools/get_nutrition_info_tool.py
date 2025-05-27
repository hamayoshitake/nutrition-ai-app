from agents import function_tool
from typing import Any, Dict, Optional, List
from services.nutrition_search_service import NutritionSearchService
from services.nutrition_details_service import NutritionDetailsService
from services.nutrition_summary_service import NutritionSummaryService

@function_tool(strict_mode=False)
def get_nutrition_info_tool(
    query: str,
    fdc_id: Optional[int] = None,
    data_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    食材の栄養情報を一括取得します。
    検索→詳細取得→整理まで自動実行し、整理された栄養情報を返します。
    
    Args:
        query: 検索クエリ（食材名）
        fdc_id: 既知のfdcId（指定時は検索をスキップ）
        data_types: データタイプフィルタ（例: ["Foundation", "Branded"]）
    
    Returns:
        整理された栄養情報 または {"error": "..."}
    """
    search_service = NutritionSearchService()
    details_service = NutritionDetailsService()
    summary_service = NutritionSummaryService()
    
    try:
        # Step 1: fdcIdの取得（検索 or 直接指定）
        if fdc_id:
            print(f"🎯 fdcId指定: {fdc_id}")
            target_fdc_id = fdc_id
            description = f"fdcId: {fdc_id}"
        else:
            print(f"🔍 検索実行: {query}")
            search_result = search_service.search(query, data_types, 5, 1)
            
            if "error" in search_result:
                error_msg = search_result.get("error", "Unknown"); return {"error": f"検索失敗: {error_msg}"}
            
            foods = search_result.get("foods", [])
            if not foods:
                return {"error": f"'{query}'の検索結果が見つかりませんでした"}
            
            target_fdc_id = foods[0]["fdcId"]
            description = foods[0].get("description", "N/A")
            print(f"✅ 検索成功: fdcId={target_fdc_id}, description={description}")
        
        # Step 2: 詳細情報取得
        print(f"📊 詳細情報取得: fdcId={target_fdc_id}")
        details = details_service.get_details(target_fdc_id)
        
        if "error" in details:
            error_msg = details.get("error", "Unknown"); return {"error": f"詳細取得失敗: {error_msg}"}
        
        # Step 3: データ整理
        print(f"🔧 栄養データ整理中...")
        summary = summary_service.summarize(details)
        
        desc = summary.get("description", "N/A"); print(f"✅ 栄養情報取得完了: {desc}")
        return {
            "success": True,
            "nutrition_info": summary,
            "fdc_id": target_fdc_id,
            "source": "USDA FoodData Central",
            "query": query
        }
        
    except Exception as e:
        print(f"❌ get_nutrition_info_tool エラー: {str(e)}")
        return {"error": f"処理中にエラーが発生しました: {str(e)}"}
