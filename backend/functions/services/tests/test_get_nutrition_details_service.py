#!/usr/bin/env python3
"""
統合ツールのサービス部分のみをテストするスクリプト
OpenAI APIキーを使わずに、各サービスの動作確認を行います
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# backend/functions 直下をモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services.nutrition_search_service import NutritionSearchService
from services.nutrition_details_service import NutritionDetailsService
from services.nutrition_summary_service import NutritionSummaryService

def test_search_service():
    """検索サービスのテスト"""
    print("🔍 === 検索サービステスト ===")
    
    search_service = NutritionSearchService()
    test_queries = ["apple", "banana", "chicken breast"]
    
    for query in test_queries:
        print(f"\n📝 検索クエリ: {query}")
        try:
            result = search_service.search(query, None, 5, 1)
            
            if "error" in result:
                print(f"❌ 検索失敗: {result['error']}")
            else:
                foods = result.get("foods", [])
                print(f"✅ 検索成功: {len(foods)}件の結果")
                if foods:
                    first_food = foods[0]
                    print(f"📊 最初の結果: fdcId={first_food.get('fdcId')}, description={first_food.get('description', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ 例外発生: {str(e)}")

def test_details_service():
    """詳細サービスのテスト（既知のfdcIdを使用）"""
    print("\n📊 === 詳細サービステスト ===")
    
    details_service = NutritionDetailsService()
    # 既知のfdcId（りんご）を使用
    test_fdc_ids = [171688, 173944]  # りんご、バナナ
    
    for fdc_id in test_fdc_ids:
        print(f"\n📝 fdcId: {fdc_id}")
        try:
            result = details_service.get_details(fdc_id)
            
            if "error" in result:
                print(f"❌ 詳細取得失敗: {result['error']}")
            else:
                print(f"✅ 詳細取得成功")
                print(f"📊 説明: {result.get('description', 'N/A')}")
                print(f"📊 データタイプ: {result.get('dataType', 'N/A')}")
                
                # 栄養素の数を確認
                nutrients = result.get('foodNutrients', [])
                print(f"📊 栄養素数: {len(nutrients)}個")
                
        except Exception as e:
            print(f"❌ 例外発生: {str(e)}")

def test_summary_service():
    """要約サービスのテスト（サンプルデータを使用）"""
    print("\n🔧 === 要約サービステスト ===")
    
    summary_service = NutritionSummaryService()
    
    # サンプルのUSDAデータ（りんごの簡略版）
    sample_data = {
        "description": "Apples, raw, with skin",
        "dataType": "Foundation",
        "foodNutrients": [
            {"nutrient": {"id": 1008, "name": "Energy"}, "amount": 52.0, "unitName": "kcal"},
            {"nutrient": {"id": 1003, "name": "Protein"}, "amount": 0.26, "unitName": "g"},
            {"nutrient": {"id": 1005, "name": "Carbohydrate, by difference"}, "amount": 13.81, "unitName": "g"},
            {"nutrient": {"id": 1004, "name": "Total lipid (fat)"}, "amount": 0.17, "unitName": "g"},
            {"nutrient": {"id": 1079, "name": "Fiber, total dietary"}, "amount": 2.4, "unitName": "g"},
            {"nutrient": {"id": 1087, "name": "Calcium, Ca"}, "amount": 6.0, "unitName": "mg"},
            {"nutrient": {"id": 1089, "name": "Iron, Fe"}, "amount": 0.12, "unitName": "mg"}
        ]
    }
    
    print(f"📝 サンプルデータ: {sample_data['description']}")
    try:
        result = summary_service.summarize(sample_data)
        
        print(f"✅ 要約成功")
        print(f"📊 説明: {result.get('description', 'N/A')}")
        print(f"📊 カロリー: {result.get('energy_kcal', 'N/A')} kcal")
        print(f"📊 タンパク質: {result.get('protein_g', 'N/A')} g")
        print(f"📊 炭水化物: {result.get('carbohydrates_g', 'N/A')} g")
        print(f"📊 脂質: {result.get('fat_g', 'N/A')} g")
        print(f"📊 食物繊維: {result.get('fiber_g', 'N/A')} g")
        print(f"📊 カルシウム: {result.get('calcium_mg', 'N/A')} mg")
        print(f"📊 鉄: {result.get('iron_mg', 'N/A')} mg")
        
    except Exception as e:
        print(f"❌ 例外発生: {str(e)}")

def test_integrated_workflow():
    """統合ワークフローのテスト（検索→詳細→要約）"""
    print("\n🔄 === 統合ワークフローテスト ===")
    
    search_service = NutritionSearchService()
    details_service = NutritionDetailsService()
    summary_service = NutritionSummaryService()
    
    query = "apple"
    print(f"📝 統合テストクエリ: {query}")
    
    try:
        # Step 1: 検索
        print(f"🔍 Step 1: 検索実行")
        search_result = search_service.search(query, None, 5, 1)
        
        if "error" in search_result:
            print(f"❌ 検索失敗: {search_result['error']}")
            return
        
        foods = search_result.get("foods", [])
        if not foods:
            print(f"❌ 検索結果なし")
            return
        
        target_fdc_id = foods[0]["fdcId"]
        description = foods[0].get("description", "N/A")
        print(f"✅ 検索成功: fdcId={target_fdc_id}, description={description}")
        
        # Step 2: 詳細取得
        print(f"📊 Step 2: 詳細情報取得")
        details = details_service.get_details(target_fdc_id)
        
        if "error" in details:
            print(f"❌ 詳細取得失敗: {details['error']}")
            return
        
        print(f"✅ 詳細取得成功")
        
        # Step 3: 要約
        print(f"🔧 Step 3: データ整理")
        summary = summary_service.summarize(details)
        
        print(f"✅ 統合ワークフロー完了")
        print(f"📊 最終結果:")
        print(f"  - 説明: {summary.get('description', 'N/A')}")
        print(f"  - カロリー: {summary.get('energy_kcal', 'N/A')} kcal")
        print(f"  - タンパク質: {summary.get('protein_g', 'N/A')} g")
        print(f"  - 炭水化物: {summary.get('carbohydrates_g', 'N/A')} g")
        print(f"  - 脂質: {summary.get('fat_g', 'N/A')} g")
        
        return {
            "success": True,
            "nutrition_info": summary,
            "fdc_id": target_fdc_id,
            "source": "USDA FoodData Central",
            "query": query
        }
        
    except Exception as e:
        print(f"❌ 統合ワークフローエラー: {str(e)}")
        return {"error": f"処理中にエラーが発生しました: {str(e)}"}

if __name__ == "__main__":
    print("🚀 サービス単体テスト開始")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 検索サービステスト
    test_search_service()
    
    # 2. 詳細サービステスト
    test_details_service()
    
    # 3. 要約サービステスト
    test_summary_service()
    
    # 4. 統合ワークフローテスト
    test_integrated_workflow()
    
    print(f"\n⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ 全サービステスト完了") 