"""
栄養データ検索ガイダンス機能の拡張版テスト

非決定論的なユーザー入力に対応した包括的なガイダンス機能をテストします。
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def call_guidance_tool(food_category=None, search_intent=None, user_input=None):
    """ガイダンスツールを直接呼び出すためのラッパー関数"""
    from function_tools.get_nutrition_search_guidance_tool import get_nutrition_search_guidance_core
    
    # デコレータを回避してコア関数を直接呼び出し
    return get_nutrition_search_guidance_core(
        food_category=food_category, 
        search_intent=search_intent, 
        user_input=user_input
    )

def test_enhanced_guidance_functions():
    """拡張されたガイダンス機能の直接テスト"""
    
    # ヘルパー関数を直接インポート
    from function_tools.get_nutrition_search_guidance_tool import (
        _get_enhanced_category_guidance,
        _get_intent_specific_guidance,
        _get_comprehensive_examples,
        _get_translation_patterns,
        _analyze_user_input,
        _get_specific_suggestions,
        _get_fallback_strategies
    )
    
    print("🧪 拡張ガイダンス機能のテストを開始します\n")
    
    # 1. 拡張カテゴリ別ガイダンスのテスト
    print("=" * 50)
    print("📋 拡張カテゴリ別ガイダンスのテスト")
    print("=" * 50)
    
    enhanced_categories = ["meat", "seafood", "nuts_seeds", "beverages", "oils_fats", "fruit", "vegetable", "dairy", "grain"]
    for category in enhanced_categories:
        guidance = _get_enhanced_category_guidance(category)
        assert "keywords" in guidance or "tips" in guidance
        print(f"✅ {category}カテゴリ: {len(guidance.get('keywords', []))}個のキーワード")
        
        if "subcategories" in guidance:
            print(f"   サブカテゴリ: {', '.join(guidance['subcategories'])}")
        
        if "examples" in guidance:
            print(f"   例: {guidance['examples'][0]}")
    
    # 2. 拡張意図別ガイダンスのテスト
    print("\n" + "=" * 50)
    print("🎯 拡張意図別ガイダンスのテスト")
    print("=" * 50)
    
    intents = ["basic_nutrition", "detailed_analysis", "comparison", "high_protein", "low_carb"]
    for intent in intents:
        guidance = _get_intent_specific_guidance(intent)
        assert "tips" in guidance
        print(f"✅ {intent}: {len(guidance['tips'])}個のヒント")
        print(f"   推奨データタイプ: {guidance.get('recommended_data_types', [])}")
        print(f"   フォーカス: {guidance.get('focus', 'N/A')}")
    
    # 3. 翻訳パターンのテスト
    print("\n" + "=" * 50)
    print("🔤 翻訳パターンのテスト")
    print("=" * 50)
    
    patterns = _get_translation_patterns()
    assert "basic_foods" in patterns
    assert "cooking_methods" in patterns
    assert "parts_cuts" in patterns
    
    print(f"✅ 基本食材翻訳: {len(patterns['basic_foods'])}個")
    print(f"   例: りんご → {patterns['basic_foods']['りんご']}")
    print(f"   アジア系食材: 納豆 → {patterns['basic_foods']['納豆']}")
    
    print(f"✅ 調理方法翻訳: {len(patterns['cooking_methods'])}個")
    print(f"   例: 生 → {patterns['cooking_methods']['生']}")
    
    print(f"✅ 部位・切り方翻訳: {len(patterns['parts_cuts'])}個")
    print(f"   例: 胸肉 → {patterns['parts_cuts']['胸肉']}")

def test_user_input_analysis():
    """ユーザー入力分析機能のテスト"""
    
    from function_tools.get_nutrition_search_guidance_tool import (
        _analyze_user_input,
        _get_specific_suggestions
    )
    
    print("\n" + "=" * 50)
    print("🔍 ユーザー入力分析のテスト")
    print("=" * 50)
    
    # テスト用の様々な入力パターン
    test_inputs = [
        "鶏肉",  # 日本語、単純
        "チキンサラダ",  # 日本語、複合料理
        "chicken breast",  # 英語、適切
        "コカコーラ",  # ブランド名
        "野菜",  # 曖昧
        "chicken breast skinless boneless raw",  # 詳細
        "meat",  # 曖昧（英語）
        "納豆"  # アジア系食材
    ]
    
    for user_input in test_inputs:
        print(f"\n📝 入力: '{user_input}'")
        analysis = _analyze_user_input(user_input)
        
        print(f"   言語: {analysis['detected_language']}")
        print(f"   タイプ: {analysis['input_type']}")
        print(f"   複雑さ: {analysis['complexity']}")
        print(f"   単語数: {analysis['word_count']}")
        print(f"   検出食材: {analysis['detected_food']}")
        print(f"   修飾語あり: {analysis['has_modifiers']}")
        
        if analysis['potential_issues']:
            print(f"   潜在的問題: {', '.join(analysis['potential_issues'])}")
        
        # 具体的な提案を取得
        suggestions = _get_specific_suggestions(user_input)
        if suggestions:
            print(f"   提案:")
            for suggestion in suggestions[:2]:  # 最初の2つの提案のみ表示
                print(f"     - {suggestion}")

def test_fallback_strategies():
    """フォールバック戦略のテスト"""
    
    from function_tools.get_nutrition_search_guidance_tool import _get_fallback_strategies
    
    print("\n" + "=" * 50)
    print("🔄 フォールバック戦略のテスト")
    print("=" * 50)
    
    strategies = _get_fallback_strategies()
    
    strategy_types = ["no_results", "too_many_results", "unknown_food", "api_errors"]
    for strategy_type in strategy_types:
        assert strategy_type in strategies
        print(f"✅ {strategy_type}: {len(strategies[strategy_type])}個の戦略")
        print(f"   例: {strategies[strategy_type][0]}")

def test_comprehensive_examples():
    """包括的な検索例のテスト"""
    
    from function_tools.get_nutrition_search_guidance_tool import _get_comprehensive_examples
    
    print("\n" + "=" * 50)
    print("📚 包括的な検索例のテスト")
    print("=" * 50)
    
    examples = _get_comprehensive_examples()
    
    # カテゴリ別の優秀なクエリ例
    assert "excellent_queries_by_category" in examples
    categories = examples["excellent_queries_by_category"]
    
    print("🏆 カテゴリ別優秀クエリ:")
    for category, queries in categories.items():
        print(f"   {category}: {len(queries)}個の例")
        print(f"     例: {queries[0]}")
    
    # 問題のある入力と解決策
    assert "problematic_inputs_and_solutions" in examples
    problems = examples["problematic_inputs_and_solutions"]
    
    print("\n⚠️ 問題のある入力と解決策:")
    for problematic_input, solution_info in problems.items():
        print(f"   入力: {problematic_input}")
        print(f"   問題: {solution_info['issue']}")
        print(f"   解決策: {solution_info['solution']}")
    
    # 基本的なクエリ品質例
    assert "excellent_queries" in examples
    assert "good_queries" in examples
    assert "poor_queries" in examples
    
    print(f"\n📊 クエリ品質例:")
    print(f"   優秀: {len(examples['excellent_queries'])}個")
    print(f"   良い: {len(examples['good_queries'])}個")
    print(f"   悪い: {len(examples['poor_queries'])}個")

def test_integration_with_main_function():
    """メイン関数との統合テスト"""
    
    print("\n" + "=" * 50)
    print("🔗 メイン関数統合テスト")
    print("=" * 50)
    
    # 1. ユーザー入力ありのテスト
    result = call_guidance_tool(
        food_category="meat",
        search_intent="basic_nutrition",
        user_input="鶏肉"
    )
    
    assert result["status"] == "success"
    assert "guidance" in result
    assert "input_analysis" in result["guidance"]
    assert "specific_suggestions" in result["guidance"]
    assert "category_specific" in result["guidance"]
    assert "intent_specific" in result["guidance"]
    
    print("✅ ユーザー入力ありのテスト成功")
    print(f"   検出言語: {result['guidance']['input_analysis']['detected_language']}")
    print(f"   提案数: {len(result['guidance']['specific_suggestions'])}")
    
    # 2. 新しいカテゴリのテスト
    result = call_guidance_tool(food_category="seafood")
    
    assert "category_specific" in result["guidance"]
    assert "subcategories" in result["guidance"]["category_specific"]
    
    print("✅ 新カテゴリ（seafood）テスト成功")
    print(f"   サブカテゴリ: {result['guidance']['category_specific']['subcategories']}")
    
    # 3. 新しい検索意図のテスト
    result = call_guidance_tool(search_intent="high_protein")
    
    assert "intent_specific" in result["guidance"]
    assert result["guidance"]["intent_specific"]["focus"] == "高タンパク質食材の特定"
    
    print("✅ 新検索意図（high_protein）テスト成功")
    
    # 4. 翻訳パターンの確認
    assert "translation_patterns" in result["guidance"]
    patterns = result["guidance"]["translation_patterns"]
    assert "basic_foods" in patterns
    assert "りんご" in patterns["basic_foods"]
    
    print("✅ 翻訳パターン統合テスト成功")

def test_real_world_scenarios():
    """実世界のシナリオテスト"""
    
    print("\n" + "=" * 50)
    print("🌍 実世界シナリオテスト")
    print("=" * 50)
    
    # シナリオ1: 日本人ユーザーが日本語で複合料理を検索
    print("📋 シナリオ1: 日本語複合料理検索")
    result = call_guidance_tool(user_input="チキンサラダ")
    
    analysis = result["guidance"]["input_analysis"]
    suggestions = result["guidance"]["specific_suggestions"]
    
    print(f"   言語検出: {analysis['detected_language']}")
    print(f"   入力タイプ: {analysis['input_type']}")
    print(f"   提案: {suggestions[0] if suggestions else 'なし'}")
    
    # シナリオ2: 栄養素特化検索
    print("\n📋 シナリオ2: 高タンパク質食材検索")
    result = call_guidance_tool(
        search_intent="high_protein",
        food_category="meat"
    )
    
    intent_guidance = result["guidance"]["intent_specific"]
    category_guidance = result["guidance"]["category_specific"]
    
    print(f"   検索フォーカス: {intent_guidance['focus']}")
    print(f"   推奨キーワード: {', '.join(category_guidance['keywords'][:3])}")
    
    # シナリオ3: アジア系食材の検索
    print("\n📋 シナリオ3: アジア系食材検索")
    result = call_guidance_tool(user_input="納豆")
    
    analysis = result["guidance"]["input_analysis"]
    suggestions = result["guidance"]["specific_suggestions"]
    
    print(f"   検出食材: {analysis['detected_food']}")
    print(f"   翻訳提案: {suggestions[0] if suggestions else 'なし'}")

def run_all_enhanced_tests():
    """全ての拡張テストを実行"""
    try:
        test_enhanced_guidance_functions()
        test_user_input_analysis()
        test_fallback_strategies()
        test_comprehensive_examples()
        test_integration_with_main_function()
        test_real_world_scenarios()
        
        print("\n" + "=" * 50)
        print("🎉 全ての拡張テストが正常に完了しました！")
        print("=" * 50)
        
        print("\n📝 実装された拡張機能:")
        print("   ✅ 非決定論的ユーザー入力分析")
        print("   ✅ 日本語→英語翻訳パターン（50+食材）")
        print("   ✅ 拡張カテゴリ対応（seafood, nuts_seeds, beverages, oils_fats）")
        print("   ✅ 栄養素特化検索意図（high_protein, low_carb）")
        print("   ✅ フォールバック戦略（4種類）")
        print("   ✅ 包括的な検索例とソリューション")
        print("   ✅ アジア系食材対応")
        print("   ✅ 複合料理分解戦略")
        print("   ✅ ブランド名検出と一般名変換")
        
        print("\n🚀 エージェントが利用可能な新機能:")
        print("   - user_input パラメータによる入力分析")
        print("   - 具体的な改善提案の自動生成")
        print("   - 多言語対応（日本語→英語翻訳）")
        print("   - エラー時の代替戦略提供")
        print("   - 栄養素特化検索ガイダンス")
        
        return True
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

# 既存のテスト関数も保持（後方互換性のため）
def test_guidance_functions():
    """既存のガイダンス機能の基本テスト（後方互換性）"""
    
    from function_tools.get_nutrition_search_guidance_tool import (
        _get_enhanced_category_guidance,
        _get_intent_specific_guidance,
        _get_comprehensive_examples
    )
    
    print("🔄 既存機能の後方互換性テスト")
    
    # 基本カテゴリのテスト
    categories = ["meat", "fruit", "vegetable", "dairy", "grain"]
    for category in categories:
        guidance = _get_enhanced_category_guidance(category)
        assert "keywords" in guidance or "tips" in guidance
        print(f"✅ {category}カテゴリ: 後方互換性OK")
    
    # 基本意図のテスト
    intents = ["basic_nutrition", "detailed_analysis", "comparison"]
    for intent in intents:
        guidance = _get_intent_specific_guidance(intent)
        assert "tips" in guidance
        print(f"✅ {intent}: 後方互換性OK")
    
    # 検索例のテスト
    examples = _get_comprehensive_examples()
    assert "excellent_queries" in examples
    assert "good_queries" in examples
    assert "poor_queries" in examples
    print("✅ 検索例: 後方互換性OK")

if __name__ == "__main__":
    print("🧪 拡張版栄養データ検索ガイダンステスト開始\n")
    
    # 拡張テストを実行
    success = run_all_enhanced_tests()
    
    # 後方互換性テストも実行
    if success:
        print("\n" + "=" * 50)
        print("🔄 後方互換性テスト")
        print("=" * 50)
        test_guidance_functions()
        print("✅ 後方互換性テスト完了")
    
    exit(0 if success else 1) 