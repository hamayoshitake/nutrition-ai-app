#!/usr/bin/env python3
"""
拡張版栄養データ検索評価ツールのテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_tools.evaluate_nutrition_search_tool import evaluate_nutrition_search_tool_core

def call_evaluation_tool(query, search_results, target_food=None, evaluation_focus=None):
    """評価ツールを呼び出すヘルパー関数"""
    return evaluate_nutrition_search_tool_core(query, search_results, target_food, evaluation_focus)

def test_enhanced_evaluation():
    """拡張版評価機能のテスト"""
    
    print("🧪 拡張版栄養データ検索評価ツールのテスト")
    print("=" * 60)
    
    # テストケース1: 高品質な検索結果
    print("\n📊 テストケース1: 高品質な検索結果")
    print("-" * 40)
    
    high_quality_results = {
        "foods": [
            {
                "fdcId": 171077,
                "description": "Chicken, broilers or fryers, breast, meat only, cooked, roasted",
                "dataType": "Foundation",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 165},
                    {"nutrientName": "Protein", "value": 31.02},
                    {"nutrientName": "Total lipid (fat)", "value": 3.57},
                    {"nutrientName": "Carbohydrate, by difference", "value": 0},
                    {"nutrientName": "Fiber, total dietary", "value": 0},
                    {"nutrientName": "Calcium, Ca", "value": 15},
                    {"nutrientName": "Iron, Fe", "value": 1.04},
                    {"nutrientName": "Sodium, Na", "value": 74}
                ]
            },
            {
                "fdcId": 171078,
                "description": "Chicken, broilers or fryers, breast, meat and skin, cooked, roasted",
                "dataType": "SR Legacy",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 197},
                    {"nutrientName": "Protein", "value": 29.8},
                    {"nutrientName": "Total lipid (fat)", "value": 7.78}
                ]
            }
        ],
        "totalHits": 25
    }
    
    result = call_evaluation_tool(
        query="chicken breast cooked",
        search_results=high_quality_results,
        target_food="chicken breast",
        evaluation_focus="accuracy"
    )
    
    print(f"✅ ステータス: {result['status']}")
    evaluation = result['evaluation']
    print(f"📈 総合スコア: {evaluation['overall_assessment']['score']:.3f}")
    print(f"🎯 グレード: {evaluation['overall_assessment']['grade']}")
    print(f"🔍 評価フォーカス: {evaluation['overall_assessment']['focus']}")
    print(f"🌐 検出言語: {evaluation['query_analysis']['language']}")
    print(f"📂 検出カテゴリ: {evaluation['query_analysis']['detected_categories']}")
    print(f"⚡ 具体性スコア: {evaluation['query_analysis']['specificity_score']:.3f}")
    print(f"🎯 関連性スコア: {evaluation['relevance_score']:.3f}")
    print(f"📊 完全性スコア: {evaluation['completeness_score']:.3f}")
    print(f"🌈 多様性スコア: {evaluation['diversity_score']:.3f}")
    
    # テストケース2: 日本語クエリ
    print("\n📊 テストケース2: 日本語クエリ")
    print("-" * 40)
    
    japanese_results = {
        "foods": [
            {
                "fdcId": 123456,
                "description": "Chicken, breast, skinless, boneless, raw",
                "dataType": "Branded",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 120},
                    {"nutrientName": "Protein", "value": 22.5}
                ]
            }
        ],
        "totalHits": 5
    }
    
    result = call_evaluation_tool(
        query="鶏肉",
        search_results=japanese_results,
        evaluation_focus="relevance"
    )
    
    evaluation = result['evaluation']
    print(f"✅ ステータス: {result['status']}")
    print(f"🌐 検出言語: {evaluation['query_analysis']['language']}")
    print(f"⚠️ 潜在的問題: {evaluation['query_analysis']['potential_issues']}")
    print(f"💡 改善提案数: {len(evaluation['improvement_suggestions'])}")
    print("📝 改善提案:")
    for i, suggestion in enumerate(evaluation['improvement_suggestions'][:3], 1):
        print(f"   {i}. {suggestion}")
    
    # テストケース3: 低品質な検索結果
    print("\n📊 テストケース3: 低品質な検索結果")
    print("-" * 40)
    
    low_quality_results = {
        "foods": [
            {
                "fdcId": 789012,
                "description": "Generic food item",
                "dataType": "Branded",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 100}
                ]
            }
        ],
        "totalHits": 1
    }
    
    result = call_evaluation_tool(
        query="meat",
        search_results=low_quality_results,
        evaluation_focus="completeness"
    )
    
    evaluation = result['evaluation']
    print(f"✅ ステータス: {result['status']}")
    print(f"📈 総合スコア: {evaluation['overall_assessment']['score']:.3f}")
    print(f"🎯 グレード: {evaluation['overall_assessment']['grade']}")
    print(f"⚠️ 品質問題: {evaluation['query_analysis']['potential_issues']}")
    print(f"📊 データタイプ分布: {evaluation['data_type_distribution']['distribution']}")
    
    # テストケース4: エラーケース
    print("\n📊 テストケース4: エラーケース")
    print("-" * 40)
    
    error_results = {
        "error": "API connection failed"
    }
    
    result = call_evaluation_tool(
        query="apple",
        search_results=error_results
    )
    
    print(f"✅ ステータス: {result['status']}")
    print(f"❌ エラー: {result.get('error', 'なし')}")
    
    # テストケース5: 詳細分析機能
    print("\n📊 テストケース5: 詳細分析機能")
    print("-" * 40)
    
    detailed_results = {
        "foods": [
            {
                "fdcId": 171077,
                "description": "Chicken, broilers or fryers, breast, meat only, cooked, roasted",
                "dataType": "Foundation",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 165},
                    {"nutrientName": "Protein", "value": 31.02},
                    {"nutrientName": "Total lipid (fat)", "value": 3.57},
                    {"nutrientName": "Carbohydrate, by difference", "value": 0},
                    {"nutrientName": "Fiber, total dietary", "value": 0},
                    {"nutrientName": "Calcium, Ca", "value": 15},
                    {"nutrientName": "Iron, Fe", "value": 1.04},
                    {"nutrientName": "Sodium, Na", "value": 74},
                    {"nutrientName": "Vitamin C, total ascorbic acid", "value": 0},
                    {"nutrientName": "Thiamin", "value": 0.068}
                ]
            }
        ],
        "totalHits": 15
    }
    
    result = call_evaluation_tool(
        query="chicken breast roasted",
        search_results=detailed_results,
        target_food="roasted chicken breast",
        evaluation_focus="balanced"
    )
    
    evaluation = result['evaluation']
    detailed_analysis = evaluation['detailed_analysis']
    
    print(f"✅ ステータス: {result['status']}")
    print(f"🧠 クエリ洞察:")
    print(f"   強み: {detailed_analysis['query_insights']['strengths']}")
    print(f"   弱み: {detailed_analysis['query_insights']['weaknesses']}")
    print(f"   最適化可能性: {detailed_analysis['query_insights']['optimization_potential']}")
    
    print(f"📊 結果洞察:")
    print(f"   データ品質評価: {detailed_analysis['result_insights']['data_quality_assessment']}")
    print(f"   栄養カバレッジ: {detailed_analysis['result_insights']['nutrition_coverage']:.3f}")
    
    print(f"📈 パフォーマンス指標:")
    metrics = detailed_analysis['performance_metrics']
    for metric, value in metrics.items():
        print(f"   {metric}: {value:.3f}")
    
    print(f"📋 推奨事項数: {len(result['recommendations'])}")
    print(f"🚀 次のステップ数: {len(result['next_steps'])}")
    
    print("\n🎉 すべてのテストが完了しました！")

def test_evaluation_focus_variations():
    """評価フォーカスのバリエーションテスト"""
    
    print("\n🎯 評価フォーカスのバリエーションテスト")
    print("=" * 50)
    
    sample_results = {
        "foods": [
            {
                "fdcId": 171077,
                "description": "Chicken, broilers or fryers, breast, meat only, cooked, roasted",
                "dataType": "Foundation",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 165},
                    {"nutrientName": "Protein", "value": 31.02},
                    {"nutrientName": "Total lipid (fat)", "value": 3.57}
                ]
            }
        ],
        "totalHits": 10
    }
    
    focus_options = ["accuracy", "completeness", "relevance", "balanced"]
    
    for focus in focus_options:
        print(f"\n📊 フォーカス: {focus}")
        print("-" * 30)
        
        result = call_evaluation_tool(
            query="chicken breast",
            search_results=sample_results,
            evaluation_focus=focus
        )
        
        evaluation = result['evaluation']
        print(f"総合スコア: {evaluation['overall_assessment']['score']:.3f}")
        print(f"グレード: {evaluation['overall_assessment']['grade']}")
        print(f"フォーカス: {evaluation['overall_assessment']['focus']}")

def test_language_detection():
    """言語検出機能のテスト"""
    
    print("\n🌐 言語検出機能のテスト")
    print("=" * 40)
    
    test_queries = [
        ("chicken breast", "english"),
        ("鶏肉", "japanese"),
        ("チキンサラダ", "japanese"),
        ("apple", "english"),
        ("りんご", "japanese"),
        ("salmon fillet", "english")
    ]
    
    sample_results = {
        "foods": [
            {
                "fdcId": 123,
                "description": "Test food",
                "dataType": "Foundation",
                "foodNutrients": [{"nutrientName": "Energy", "value": 100}]
            }
        ],
        "totalHits": 1
    }
    
    for query, expected_lang in test_queries:
        result = call_evaluation_tool(
            query=query,
            search_results=sample_results
        )
        
        detected_lang = result['evaluation']['query_analysis']['language']
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"{status} '{query}' → 検出: {detected_lang}, 期待: {expected_lang}")

if __name__ == "__main__":
    test_enhanced_evaluation()
    test_evaluation_focus_variations()
    test_language_detection() 