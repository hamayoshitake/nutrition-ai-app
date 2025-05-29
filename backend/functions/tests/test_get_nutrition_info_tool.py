#!/usr/bin/env python3
"""
栄養検索ガイダンス・評価ツールを使用するエージェントの統合テスト
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# backend/functions 直下をモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from agents import Agent, Runner
from function_tools.get_nutrition_info_tool import get_nutrition_info_tool
from function_tools.nutrition_tools import save_nutrition_entry_tool
from function_tools.get_nutrition_search_guidance_tool import get_nutrition_search_guidance_tool
from function_tools.evaluate_nutrition_search_tool import evaluate_nutrition_search_tool

# テスト用エージェント（統合ツール使用）
test_agent = Agent(
    name="TestAgent",
    model="gpt-4o-mini",
    instructions="""
    栄養情報テスト用エージェントです。
    
    動作ルール：
    1. 栄養情報を聞かれた場合は、get_nutrition_info_toolで一括取得してください
        - **重要：日本語の食材名の場合は、まず英語に翻訳してからツールを使用してください**
        - 翻訳例：
            * りんご → apple
            * バナナ → banana
            * 鶏胸肉 → chicken breast
            * 鶏肉 → chicken
            * 牛肉 → beef
            * 豚肉 → pork
            * 卵 → egg
            * ご飯 → rice
            * パン → bread
            * 牛乳 → milk
    2. このツールは検索→詳細取得→整理まで自動実行します
    3. 取得した情報を分かりやすく整理して回答してください
    4. エラーが発生した場合は、エラー内容を報告してください
    5. ツールから取得できなかった場合は、final_outputに『api失敗』と文字列で返してください
    """,
    tools=[get_nutrition_info_tool, save_nutrition_entry_tool]
)

# 新しい統合テスト用エージェント（ガイダンス・評価ツール使用）
guidance_evaluation_agent = Agent(
    name="GuidanceEvaluationAgent",
    model="gpt-4o-mini",
    instructions="""
    栄養検索ガイダンス・評価専門エージェントです。
    
    動作ルール：
    1. 検索ガイダンスが必要な場合：
       - get_nutrition_search_guidance_toolを使用してガイダンスを取得
       - 食材カテゴリ、検索意図、ユーザー入力を適切に分析
       - 日本語入力の場合は翻訳提案を含める
    
    2. 検索結果の評価が必要な場合：
       - evaluate_nutrition_search_toolを使用して結果を評価
       - 精度、完全性、関連性を総合的に評価
       - 改善提案を具体的に提示
    
    3. 統合ワークフロー：
       - ガイダンス取得 → 検索実行 → 結果評価 → 改善提案
       - 各ステップの結果を詳細に報告
       - エラー時は適切なフォールバック戦略を提示
    
    4. 応答形式：
       - 各ツールの実行結果を構造化して報告
       - スコアやグレードを分かりやすく表示
       - 次のアクションを明確に提示
    """,
    tools=[get_nutrition_search_guidance_tool, evaluate_nutrition_search_tool]
)

async def test_nutrition_agent():
    """統合ツールを使用するエージェントのテスト"""
    print("🧪 === 新しい統合ツール検証開始 ===")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # テストケース
    test_cases = [
        {
            "prompt": "りんごの栄養価を教えて",
            "expected_tool": "get_nutrition_info_tool",
            "description": "栄養情報問い合わせテスト"
        },
        {
            "prompt": "バナナのカロリーを知りたい",
            "expected_tool": "get_nutrition_info_tool",
            "description": "カロリー問い合わせテスト"
        },
        {
            "prompt": "鶏胸肉の栄養成分を調べて",
            "expected_tool": "get_nutrition_info_tool",
            "description": "栄養成分問い合わせテスト"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 === テストケース {i}: {test_case['description']} ===")
        print(f"📝 プロンプト: {test_case['prompt']}")
        print(f"🎯 期待ツール: {test_case['expected_tool']}")
        
        try:
            # メッセージ形式
            messages = [
                {"role": "user", "content": test_case['prompt']}
            ]
            
            # エージェント実行
            result = await Runner.run(test_agent, messages)

            # new_itemsの条件分岐処理
            if hasattr(result, 'new_items') and result.new_items:
                for idx, item in enumerate(result.new_items):
                    # itemがツール呼び出し情報を含むかチェック
                    if hasattr(item, 'tool_name'):
                        print(f"    - Tool Name: {item.tool_name}")
                    if hasattr(item, 'function_calls'):
                        print(f"    - Function Calls: {item.function_calls}")
                        
            elif hasattr(result, 'new_items'):
                print("⚠️ new_itemsは存在しますが、内容が空です")
                print(f"📊 new_items値: {result.new_items}")
            else:
                print("❌ new_items属性が存在しません")
            
            print(f"✅ 実行成功")
            print(f"🤖 エージェント応答: {result.final_output[:300]}...")
            
        except Exception as e:
            print(f"❌ エラー発生: {str(e)}")
            print(f"❌ エラータイプ: {type(e).__name__}")
    
    print(f"\n🏁 === 検証完了 ===")
    print(f"⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def test_guidance_evaluation_agent():
    """ガイダンス・評価ツールを使用するエージェントのテスト"""
    print("\n🔬 === ガイダンス・評価エージェント統合テスト開始 ===")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # テストケース
    test_cases = [
        {
            "prompt": "鶏肉の栄養検索でより良い結果を得るためのガイダンスを教えて",
            "expected_tools": ["get_nutrition_search_guidance_tool"],
            "description": "検索ガイダンス取得テスト"
        },
        {
            "prompt": "「chicken」で検索した結果を評価してください。結果は10件で、Foundation データが3件、Branded データが7件でした",
            "expected_tools": ["evaluate_nutrition_search_tool"],
            "description": "検索結果評価テスト"
        },
        {
            "prompt": "日本語で「りんご」と検索したいのですが、どのようにすれば良い結果が得られますか？その後、実際の検索結果も評価してください",
            "expected_tools": ["get_nutrition_search_guidance_tool", "evaluate_nutrition_search_tool"],
            "description": "ガイダンス→評価の統合ワークフローテスト"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 === テストケース {i}: {test_case['description']} ===")
        print(f"📝 プロンプト: {test_case['prompt']}")
        print(f"🎯 期待ツール: {', '.join(test_case['expected_tools'])}")
        
        try:
            # メッセージ形式
            messages = [
                {"role": "user", "content": test_case['prompt']}
            ]
            
            # エージェント実行
            result = await Runner.run(guidance_evaluation_agent, messages)
            
            print(f"✅ 実行成功")
            print(f"🤖 エージェント応答: {result.final_output[:500]}...")
            
            # ツール使用状況の確認
            if hasattr(result, 'new_items') and result.new_items:
                print(f"🔧 使用されたツール数: {len(result.new_items)}")
                for idx, item in enumerate(result.new_items):
                    if hasattr(item, 'tool_name'):
                        print(f"    {idx + 1}. {item.tool_name}")
            
        except Exception as e:
            print(f"❌ エラー発生: {str(e)}")
            print(f"❌ エラータイプ: {type(e).__name__}")
    
    print(f"\n🏁 === ガイダンス・評価テスト完了 ===")
    print(f"⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def test_integrated_workflow():
    """統合ワークフローテスト"""
    print("\n🔄 === 統合ワークフローテスト開始 ===")
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 複雑なワークフローテスト
    workflow_scenarios = [
        {
            "prompt": """
            以下のシナリオを実行してください：
            1. 「鶏胸肉」の栄養検索に関するガイダンスを取得
            2. 模擬検索結果を評価（クエリ: "chicken breast", 結果: 5件のFoundationデータ）
            3. 改善提案を提示
            """,
            "description": "完全統合ワークフロー"
        },
        {
            "prompt": """
            高タンパク質食材の検索戦略について：
            1. 高タンパク質食材検索のガイダンスを取得
            2. 「protein rich foods」での検索結果を評価
            3. より良い検索戦略を提案
            """,
            "description": "特化検索戦略テスト"
        }
    ]
    
    for i, scenario in enumerate(workflow_scenarios, 1):
        print(f"\n🎭 === ワークフローシナリオ {i}: {scenario['description']} ===")
        print(f"📋 シナリオ: {scenario['prompt'][:100]}...")
        
        try:
            messages = [
                {"role": "user", "content": scenario['prompt']}
            ]
            
            result = await Runner.run(guidance_evaluation_agent, messages)
            
            print(f"✅ ワークフロー実行成功")
            print(f"📊 応答長: {len(result.final_output)} 文字")
            print(f"🎯 応答概要: {result.final_output[:200]}...")
            
        except Exception as e:
            print(f"❌ ワークフローエラー: {str(e)}")
    
    print(f"\n🏁 === 統合ワークフローテスト完了 ===")

def test_tool_directly():
    """統合ツールを直接テスト"""
    print("🔧 === 統合ツール直接テスト ===")
    
    test_queries = [
        {"query": "apple", "description": "りんご"},
        {"query": "banana", "description": "バナナ"},
        {"query": "chicken breast", "description": "鶏胸肉"}
    ]
    
    for test_query in test_queries:
        print(f"\n🔍 テスト: {test_query['description']} ({test_query['query']})")
        try:
            # FunctionToolオブジェクトから実際の関数を取得
            if hasattr(get_nutrition_info_tool, 'func'):
                result = get_nutrition_info_tool.func(test_query['query'])
            else:
                # 直接呼び出しを試行
                result = get_nutrition_info_tool(test_query['query'])
                
            if result.get("success"):
                nutrition = result["nutrition_info"]
                print(f"✅ 成功: {nutrition.get('description', 'N/A')}")
                print(f"📊 カロリー: {nutrition.get('energy_kcal', 'N/A')} kcal")
                print(f"🥩 タンパク質: {nutrition.get('protein_g', 'N/A')} g")
                print(f"🍞 炭水化物: {nutrition.get('carbohydrates_g', 'N/A')} g")
                print(f"🥑 脂質: {nutrition.get('fat_g', 'N/A')} g")
            else:
                print(f"❌ 失敗: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 例外: {str(e)}")

def test_guidance_tool_directly():
    """ガイダンスツールの直接テスト"""
    print("\n🧭 === ガイダンスツール直接テスト ===")
    
    test_cases = [
        {
            "food_category": "meat",
            "search_intent": "basic_nutrition",
            "user_input": "鶏肉",
            "description": "日本語入力の基本栄養検索"
        },
        {
            "food_category": "fruit",
            "search_intent": "detailed_analysis",
            "user_input": "apple",
            "description": "英語入力の詳細分析"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 テスト: {test_case['description']}")
        try:
            if hasattr(get_nutrition_search_guidance_tool, 'func'):
                result = get_nutrition_search_guidance_tool.func(
                    food_category=test_case['food_category'],
                    search_intent=test_case['search_intent'],
                    user_input=test_case['user_input']
                )
            else:
                result = get_nutrition_search_guidance_tool(
                    food_category=test_case['food_category'],
                    search_intent=test_case['search_intent'],
                    user_input=test_case['user_input']
                )
            
            if result.get("status") == "success":
                guidance = result["guidance"]
                print(f"✅ ガイダンス取得成功")
                print(f"📋 一般的なヒント数: {len(guidance.get('general_tips', {}).get('effective_keywords', []))}")
                print(f"🎯 具体的提案数: {len(guidance.get('specific_suggestions', []))}")
                
                if guidance.get('input_analysis'):
                    analysis = guidance['input_analysis']
                    print(f"🌐 検出言語: {analysis.get('detected_language', 'unknown')}")
                    print(f"📝 入力タイプ: {analysis.get('input_type', 'unknown')}")
            else:
                print(f"❌ 失敗: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 例外: {str(e)}")

def test_evaluation_tool_directly():
    """評価ツールの直接テスト"""
    print("\n📊 === 評価ツール直接テスト ===")
    
    # 模擬検索結果
    mock_search_results = {
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
        "totalHits": 15
    }
    
    test_cases = [
        {
            "query": "chicken breast",
            "target_food": "chicken breast",
            "evaluation_focus": "accuracy",
            "description": "精度重視評価"
        },
        {
            "query": "鶏肉",
            "target_food": "chicken",
            "evaluation_focus": "completeness",
            "description": "完全性重視評価"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 テスト: {test_case['description']}")
        try:
            if hasattr(evaluate_nutrition_search_tool, 'func'):
                result = evaluate_nutrition_search_tool.func(
                    query=test_case['query'],
                    search_results=mock_search_results,
                    target_food=test_case['target_food'],
                    evaluation_focus=test_case['evaluation_focus']
                )
            else:
                result = evaluate_nutrition_search_tool(
                    query=test_case['query'],
                    search_results=mock_search_results,
                    target_food=test_case['target_food'],
                    evaluation_focus=test_case['evaluation_focus']
                )
            
            if result.get("status") == "success":
                evaluation = result["evaluation"]
                overall = evaluation["overall_assessment"]
                print(f"✅ 評価成功")
                print(f"📊 総合スコア: {overall['score']:.3f}")
                print(f"🎯 グレード: {overall['grade']}")
                print(f"📈 関連性スコア: {evaluation['relevance_score']:.3f}")
                print(f"📋 改善提案数: {len(evaluation['improvement_suggestions'])}")
            else:
                print(f"❌ 失敗: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 例外: {str(e)}")

if __name__ == "__main__":
    print("🚀 栄養検索ガイダンス・評価ツール統合テスト開始")
    
    # 1. 既存の統合ツール直接テスト
    test_tool_directly()
    
    # 2. 新しいガイダンスツール直接テスト
    test_guidance_tool_directly()
    
    # 3. 新しい評価ツール直接テスト
    test_evaluation_tool_directly()
    
    # 4. 既存エージェント経由テスト
    print("\n" + "="*60)
    asyncio.run(test_nutrition_agent())
    
    # 5. 新しいガイダンス・評価エージェント経由テスト
    print("\n" + "="*60)
    asyncio.run(test_guidance_evaluation_agent())
    
    # 6. 統合ワークフローテスト
    print("\n" + "="*60)
    asyncio.run(test_integrated_workflow())
    
    print("\n✅ 全統合テスト完了")
    print("\n📋 実装された機能:")
    print("   ✅ 栄養情報取得エージェント")
    print("   ✅ ガイダンス・評価エージェント")
    print("   ✅ 2つのツールの統合ワークフロー")
    print("   ✅ 直接ツール呼び出しテスト")
    print("   ✅ エージェント経由テスト")
    print("   ✅ 複雑なシナリオテスト")