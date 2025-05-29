#!/usr/bin/env python3
"""
栄養データ検索ガイダンスと評価ツールの統合テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_tools.get_nutrition_search_guidance_tool import get_nutrition_search_guidance_core
from function_tools.evaluate_nutrition_search_tool import evaluate_nutrition_search_tool_core

def test_guidance_evaluation_integration():
    """ガイダンスと評価の統合テスト"""
    
    print("🔗 栄養データ検索ガイダンス・評価統合テスト")
    print("=" * 60)
    
    # シナリオ1: 日本語入力からガイダンス取得→評価
    print("\n📋 シナリオ1: 日本語入力の改善プロセス")
    print("-" * 50)
    
    user_input = "鶏肉"
    print(f"👤 ユーザー入力: '{user_input}'")
    
    # ガイダンス取得
    guidance = get_nutrition_search_guidance_core(
        food_category="meat",
        search_intent="basic_nutrition",
        user_input=user_input
    )
    
    print(f"💡 ガイダンス取得: {guidance['status']}")
    if guidance['status'] == 'success':
        user_analysis = guidance['guidance'].get('input_analysis', {})
        print(f"🌐 検出言語: {user_analysis.get('detected_language', 'unknown')}")
        print(f"📝 入力タイプ: {user_analysis.get('input_type', 'unknown')}")
        
        suggestions = guidance['guidance'].get('specific_suggestions', [])
        if suggestions:
            print(f"💡 改善提案: {suggestions[0]}")
    
    # 模擬検索結果（改善前）
    poor_results = {
        "foods": [
            {
                "fdcId": 123456,
                "description": "Chicken, unspecified",
                "dataType": "Branded",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 150}
                ]
            }
        ],
        "totalHits": 1
    }
    
    # 評価（改善前）
    evaluation_before = evaluate_nutrition_search_tool_core(
        query=user_input,
        search_results=poor_results,
        evaluation_focus="accuracy"
    )
    
    print(f"\n📊 改善前の評価:")
    print(f"   スコア: {evaluation_before['evaluation']['overall_assessment']['score']:.3f}")
    print(f"   グレード: {evaluation_before['evaluation']['overall_assessment']['grade']}")
    
    # 改善後の検索結果
    improved_results = {
        "foods": [
            {
                "fdcId": 171077,
                "description": "Chicken, broilers or fryers, breast, meat only, cooked, roasted",
                "dataType": "Foundation",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 165},
                    {"nutrientName": "Protein", "value": 31.02},
                    {"nutrientName": "Total lipid (fat)", "value": 3.57},
                    {"nutrientName": "Carbohydrate, by difference", "value": 0}
                ]
            }
        ],
        "totalHits": 15
    }
    
    # 評価（改善後）
    evaluation_after = evaluate_nutrition_search_tool_core(
        query="chicken breast cooked",
        search_results=improved_results,
        target_food="chicken breast",
        evaluation_focus="accuracy"
    )
    
    print(f"\n📈 改善後の評価:")
    print(f"   スコア: {evaluation_after['evaluation']['overall_assessment']['score']:.3f}")
    print(f"   グレード: {evaluation_after['evaluation']['overall_assessment']['grade']}")
    
    improvement = evaluation_after['evaluation']['overall_assessment']['score'] - evaluation_before['evaluation']['overall_assessment']['score']
    print(f"🚀 改善度: {improvement:.3f}")
    
    # シナリオ2: 高タンパク質食材検索のワークフロー
    print("\n📋 シナリオ2: 高タンパク質食材検索ワークフロー")
    print("-" * 50)
    
    # ガイダンス取得（高タンパク質特化）
    protein_guidance = get_nutrition_search_guidance_core(
        food_category="meat",
        search_intent="high_protein"
    )
    
    print(f"💡 高タンパク質ガイダンス: {protein_guidance['status']}")
    if protein_guidance['status'] == 'success':
        intent_guidance = protein_guidance['guidance'].get('intent_specific', {})
        print(f"🎯 フォーカス: {intent_guidance.get('focus', 'unknown')}")
        
        recommended_keywords = intent_guidance.get('recommended_keywords', [])
        if recommended_keywords:
            print(f"🔑 推奨キーワード: {', '.join(recommended_keywords[:3])}")
    
    # 高タンパク質食材の検索結果
    protein_results = {
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
            },
            {
                "fdcId": 175167,
                "description": "Fish, salmon, Atlantic, farmed, cooked, dry heat",
                "dataType": "Foundation",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 206},
                    {"nutrientName": "Protein", "value": 22.1},
                    {"nutrientName": "Total lipid (fat)", "value": 12.35}
                ]
            }
        ],
        "totalHits": 25
    }
    
    # 評価（高タンパク質フォーカス）
    protein_evaluation = evaluate_nutrition_search_tool_core(
        query="chicken breast salmon high protein",
        search_results=protein_results,
        evaluation_focus="completeness"
    )
    
    print(f"\n📊 高タンパク質検索の評価:")
    print(f"   スコア: {protein_evaluation['evaluation']['overall_assessment']['score']:.3f}")
    print(f"   グレード: {protein_evaluation['evaluation']['overall_assessment']['grade']}")
    print(f"   完全性スコア: {protein_evaluation['evaluation']['completeness_score']:.3f}")
    print(f"   多様性スコア: {protein_evaluation['evaluation']['diversity_score']:.3f}")
    
    # シナリオ3: エラー処理とフォールバック
    print("\n📋 シナリオ3: エラー処理とフォールバック戦略")
    print("-" * 50)
    
    # 不明な食材でのガイダンス
    unknown_guidance = get_nutrition_search_guidance_core(
        food_category="unknown",
        search_intent="basic_nutrition",
        user_input="謎の食材"
    )
    
    print(f"❓ 不明食材ガイダンス: {unknown_guidance['status']}")
    
    # エラー結果の評価
    error_results = {
        "error": "No results found"
    }
    
    error_evaluation = evaluate_nutrition_search_tool_core(
        query="謎の食材",
        search_results=error_results
    )
    
    print(f"❌ エラー評価: {error_evaluation['status']}")
    
    # フォールバック戦略の取得
    if unknown_guidance['status'] == 'success':
        fallback_strategies = unknown_guidance['guidance'].get('fallback_strategies', {})
        if 'unknown_food' in fallback_strategies:
            strategies = fallback_strategies['unknown_food']
            print(f"🔄 フォールバック戦略数: {len(strategies)}")
            if strategies:
                print(f"💡 戦略例: {strategies[0]}")

def test_workflow_optimization():
    """ワークフロー最適化テスト"""
    
    print("\n🔧 ワークフロー最適化テスト")
    print("=" * 40)
    
    # 複数の検索戦略を比較
    test_queries = [
        ("chicken", "シンプル"),
        ("chicken breast", "部位指定"),
        ("chicken breast skinless", "詳細指定"),
        ("chicken breast skinless boneless raw", "完全指定")
    ]
    
    sample_results = {
        "foods": [
            {
                "fdcId": 171077,
                "description": "Chicken, broilers or fryers, breast, meat only, raw",
                "dataType": "Foundation",
                "foodNutrients": [
                    {"nutrientName": "Energy", "value": 165},
                    {"nutrientName": "Protein", "value": 31.02}
                ]
            }
        ],
        "totalHits": 10
    }
    
    print("\n📊 検索戦略比較:")
    for query, description in test_queries:
        evaluation = evaluate_nutrition_search_tool_core(
            query=query,
            search_results=sample_results,
            evaluation_focus="balanced"
        )
        
        score = evaluation['evaluation']['overall_assessment']['score']
        specificity = evaluation['evaluation']['query_analysis']['specificity_score']
        
        print(f"   {description:12} | スコア: {score:.3f} | 具体性: {specificity:.3f}")

def test_multilingual_workflow():
    """多言語ワークフローテスト"""
    
    print("\n🌐 多言語ワークフローテスト")
    print("=" * 40)
    
    # 日本語→英語翻訳ワークフロー
    japanese_inputs = [
        ("りんご", "apple"),
        ("鶏肉", "chicken"),
        ("サーモン", "salmon"),
        ("納豆", "natto fermented soybeans")
    ]
    
    print("\n🔄 翻訳ワークフロー:")
    for jp_input, expected_en in japanese_inputs:
        # ガイダンス取得
        guidance = get_nutrition_search_guidance_core(
            food_category="fruit" if "りんご" in jp_input else "meat",
            search_intent="basic_nutrition",
            user_input=jp_input
        )
        
        if guidance['status'] == 'success':
            analysis = guidance['guidance'].get('input_analysis', {})
            detected_foods = analysis.get('detected_food', [])
            
            print(f"   '{jp_input}' → 検出: {detected_foods}")
            
            # 翻訳提案があるかチェック
            suggestions = guidance['guidance'].get('specific_suggestions', [])
            has_translation = any('として検索' in s for s in suggestions)
            status = "✅" if has_translation else "❌"
            print(f"   {status} 翻訳提案: {'あり' if has_translation else 'なし'}")

if __name__ == "__main__":
    test_guidance_evaluation_integration()
    test_workflow_optimization()
    test_multilingual_workflow()
    
    print("\n🎉 統合テスト完了！")
    print("\n📋 実装された統合機能:")
    print("   ✅ ガイダンス→評価のワークフロー")
    print("   ✅ 改善前後の比較評価")
    print("   ✅ 特化検索意図の対応")
    print("   ✅ エラー処理とフォールバック")
    print("   ✅ 多言語対応ワークフロー")
    print("   ✅ 検索戦略の最適化支援") 