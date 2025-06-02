from agents import function_tool
from typing import Any, Dict, List, Optional
import re
from difflib import SequenceMatcher

def evaluate_nutrition_search_tool_core(
    query: str,
    search_results: Dict[str, Any],
    target_food: Optional[str] = None,
    evaluation_focus: Optional[str] = None
) -> Dict[str, Any]:
    """
    栄養データ検索結果の品質を評価し、改善提案を提供します。
    拡張版: より包括的な評価とカスタマイズ可能な評価基準
    
    Args:
        query: 使用した検索クエリ
        search_results: get_nutrition_search_tool の結果
        target_food: 探している食材名（オプション）
        evaluation_focus: 評価の重点 ('accuracy', 'completeness', 'relevance')
    
    Returns:
        評価結果と改善提案を含む辞書
    """
    
    if "error" in search_results:
        return {
            "status": "error",
            "message": "検索結果にエラーが含まれています",
            "error": search_results["error"]
        }
    
    # 検索結果の基本情報を取得
    foods = search_results.get("foods", [])
    total_hits = search_results.get("totalHits", 0)
    
    # 評価指標を計算
    evaluation = {
        "query_analysis": _analyze_query_enhanced(query),
        "result_quality": _evaluate_result_quality_enhanced(foods, query, target_food),
        "data_type_distribution": _analyze_data_types_enhanced(foods),
        "relevance_score": _calculate_relevance_score_enhanced(foods, query, target_food),
        "completeness_score": _calculate_completeness_score_enhanced(foods),
        "diversity_score": _calculate_diversity_score(foods),
        "improvement_suggestions": []
    }
    
    # 評価フォーカスに応じた重み調整
    weights = _get_evaluation_weights(evaluation_focus)
    
    # 改善提案を生成
    suggestions = _generate_improvement_suggestions_enhanced(
        query, foods, total_hits, evaluation, target_food
    )
    evaluation["improvement_suggestions"] = suggestions
    
    # 総合評価
    overall_score = _calculate_overall_score_enhanced(evaluation, weights)
    evaluation["overall_assessment"] = {
        "score": overall_score,
        "grade": _get_grade(overall_score),
        "summary": _get_assessment_summary_enhanced(overall_score, len(foods), total_hits),
        "focus": evaluation_focus or "balanced"
    }
    
    # 詳細分析
    evaluation["detailed_analysis"] = _generate_detailed_analysis(evaluation, foods)
    
    return {
        "status": "success",
        "evaluation": evaluation,
        "recommendations": _get_recommendations_enhanced(evaluation),
        "next_steps": _suggest_next_steps(evaluation, query)
    }

@function_tool(strict_mode=False)
def evaluate_nutrition_search_tool(
    query: str,
    search_results: Dict[str, Any],
    target_food: Optional[str] = None,
    evaluation_focus: Optional[str] = None
) -> Dict[str, Any]:
    """
    栄養データ検索結果の品質を評価し、改善提案を提供します。
    拡張版: より包括的な評価とカスタマイズ可能な評価基準
    
    Args:
        query: 使用した検索クエリ
        search_results: get_nutrition_search_tool の結果
        target_food: 探している食材名（オプション）
        evaluation_focus: 評価の重点 ('accuracy', 'completeness', 'relevance')
    
    Returns:
        評価結果と改善提案を含む辞書
    """
    return evaluate_nutrition_search_tool_core(query, search_results, target_food, evaluation_focus)

def _analyze_query_enhanced(query: str) -> Dict[str, Any]:
    """拡張されたクエリ分析"""
    
    words = query.lower().split()
    
    # 動的な食材検出（より包括的）
    detected_categories = _detect_food_categories(query)
    
    # 修飾語の詳細分析
    modifiers = _analyze_modifiers(words)
    
    # 言語検出
    language = _detect_language(query)
    
    analysis = {
        "word_count": len(words),
        "detected_categories": detected_categories,
        "language": language,
        "modifiers": modifiers,
        "specificity_score": _calculate_specificity_score_enhanced(words, detected_categories),
        "complexity_level": _assess_query_complexity(query),
        "potential_issues": _identify_query_issues(query, words, detected_categories)
    }
    
    return analysis

def _detect_food_categories(query: str) -> List[str]:
    """動的な食材カテゴリ検出"""
    
    categories = []
    query_lower = query.lower()
    
    # 肉類
    meat_keywords = [
        "chicken", "beef", "pork", "lamb", "turkey", "duck", "veal",
        "鶏肉", "牛肉", "豚肉", "羊肉", "七面鳥", "鴨肉"
    ]
    if any(keyword in query_lower for keyword in meat_keywords):
        categories.append("meat")
    
    # 魚介類
    seafood_keywords = [
        "fish", "salmon", "tuna", "cod", "shrimp", "crab", "lobster",
        "魚", "サーモン", "マグロ", "タラ", "エビ", "カニ", "ロブスター"
    ]
    if any(keyword in query_lower for keyword in seafood_keywords):
        categories.append("seafood")
    
    # 果物
    fruit_keywords = [
        "apple", "banana", "orange", "grape", "strawberry", "peach",
        "りんご", "バナナ", "オレンジ", "ぶどう", "いちご", "桃"
    ]
    if any(keyword in query_lower for keyword in fruit_keywords):
        categories.append("fruit")
    
    # 野菜
    vegetable_keywords = [
        "carrot", "broccoli", "spinach", "tomato", "potato", "onion",
        "にんじん", "ブロッコリー", "ほうれん草", "トマト", "じゃがいも", "玉ねぎ"
    ]
    if any(keyword in query_lower for keyword in vegetable_keywords):
        categories.append("vegetable")
    
    # 乳製品
    dairy_keywords = [
        "milk", "cheese", "yogurt", "butter", "cream",
        "牛乳", "チーズ", "ヨーグルト", "バター", "クリーム"
    ]
    if any(keyword in query_lower for keyword in dairy_keywords):
        categories.append("dairy")
    
    # 穀物
    grain_keywords = [
        "rice", "bread", "pasta", "wheat", "oats", "quinoa",
        "米", "パン", "パスタ", "小麦", "オーツ", "キヌア"
    ]
    if any(keyword in query_lower for keyword in grain_keywords):
        categories.append("grain")
    
    return categories

def _analyze_modifiers(words: List[str]) -> Dict[str, List[str]]:
    """修飾語の詳細分析"""
    
    modifiers = {
        "cooking_method": [],
        "preparation": [],
        "part": [],
        "quality": [],
        "size": []
    }
    
    # 調理方法
    cooking_methods = ["raw", "cooked", "baked", "grilled", "fried", "boiled", "steamed", "roasted"]
    modifiers["cooking_method"] = [word for word in words if word in cooking_methods]
    
    # 準備状態
    preparations = ["skinless", "boneless", "peeled", "trimmed", "whole", "ground", "chopped"]
    modifiers["preparation"] = [word for word in words if word in preparations]
    
    # 部位
    parts = ["breast", "thigh", "leg", "wing", "fillet", "loin", "shoulder"]
    modifiers["part"] = [word for word in words if word in parts]
    
    # 品質
    qualities = ["fresh", "frozen", "organic", "lean", "fat-free", "low-fat"]
    modifiers["quality"] = [word for word in words if word in qualities]
    
    # サイズ
    sizes = ["large", "medium", "small", "jumbo", "mini"]
    modifiers["size"] = [word for word in words if word in sizes]
    
    return modifiers

def _detect_language(query: str) -> str:
    """言語検出"""
    
    # 日本語文字の検出
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', query):
        return "japanese"
    else:
        return "english"

def _calculate_specificity_score_enhanced(words: List[str], categories: List[str]) -> float:
    """拡張された具体性スコア計算"""
    
    # 基本スコア（単語数ベース）
    base_score = min(len(words) * 0.15, 0.6)
    
    # カテゴリボーナス
    category_bonus = len(categories) * 0.1
    
    # 修飾語ボーナス
    all_modifiers = [
        "raw", "cooked", "fresh", "skinless", "boneless", "whole", "lean",
        "baked", "grilled", "fried", "boiled", "steamed", "roasted",
        "organic", "frozen", "large", "medium", "small"
    ]
    modifier_bonus = sum(0.05 for word in words if word in all_modifiers)
    
    # 部位ボーナス
    parts = ["breast", "thigh", "leg", "fillet", "loin", "shoulder", "wing"]
    part_bonus = sum(0.1 for word in words if word in parts)
    
    return min(base_score + category_bonus + modifier_bonus + part_bonus, 1.0)

def _assess_query_complexity(query: str) -> str:
    """クエリの複雑さを評価"""
    
    words = query.split()
    
    if len(words) <= 2:
        return "simple"
    elif len(words) <= 4:
        return "moderate"
    else:
        return "complex"

def _identify_query_issues(query: str, words: List[str], categories: List[str]) -> List[str]:
    """クエリの潜在的問題を特定"""
    
    issues = []
    
    # 基本的な問題
    if len(words) == 1:
        issues.append("クエリが短すぎる可能性があります")
    
    if not categories:
        issues.append("明確な食材カテゴリが検出されませんでした")
    
    # 言語混在の問題
    has_japanese = re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', query)
    has_english = re.search(r'[a-zA-Z]', query)
    
    if has_japanese and has_english:
        issues.append("日本語と英語が混在しています")
    
    # 曖昧な表現
    vague_terms = ["meat", "fish", "vegetable", "fruit", "肉", "魚", "野菜", "果物"]
    if any(term in query.lower() for term in vague_terms) and len(words) <= 2:
        issues.append("表現が曖昧すぎる可能性があります")
    
    return issues

def _evaluate_result_quality_enhanced(foods: List[Dict], query: str, target_food: Optional[str]) -> Dict[str, Any]:
    """拡張された結果品質評価"""
    
    if not foods:
        return {
            "result_count": 0,
            "quality_score": 0.0,
            "data_type_quality": {},
            "description_analysis": {},
            "issues": ["検索結果が見つかりませんでした"]
        }
    
    # データタイプ品質分析
    data_type_quality = _analyze_data_type_quality(foods)
    
    # 説明文分析
    description_analysis = _analyze_descriptions(foods, query, target_food)
    
    # 栄養データ完全性
    nutrition_completeness = _analyze_nutrition_completeness(foods)
    
    # 品質スコア計算
    quality_score = (
        data_type_quality["score"] * 0.3 +
        description_analysis["relevance_score"] * 0.4 +
        nutrition_completeness["score"] * 0.3
    )
    
    return {
        "result_count": len(foods),
        "quality_score": quality_score,
        "data_type_quality": data_type_quality,
        "description_analysis": description_analysis,
        "nutrition_completeness": nutrition_completeness,
        "top_results_analysis": _analyze_top_results(foods[:3], query)
    }

def _analyze_data_type_quality(foods: List[Dict]) -> Dict[str, Any]:
    """データタイプ品質分析"""
    
    data_types = {}
    for food in foods:
        data_type = food.get("dataType", "Unknown")
        data_types[data_type] = data_types.get(data_type, 0) + 1
    
    # 品質スコア（Foundation > SR Legacy > Survey > Branded）
    quality_weights = {
        "Foundation": 1.0,
        "SR Legacy": 0.8,
        "Survey (FNDDS)": 0.6,
        "Branded": 0.4
    }
    
    total_foods = len(foods)
    weighted_score = 0.0
    
    for data_type, count in data_types.items():
        weight = quality_weights.get(data_type, 0.2)
        weighted_score += (count / total_foods) * weight
    
    return {
        "distribution": data_types,
        "score": weighted_score,
        "has_foundation": "Foundation" in data_types,
        "has_sr_legacy": "SR Legacy" in data_types
    }

def _analyze_descriptions(foods: List[Dict], query: str, target_food: Optional[str]) -> Dict[str, Any]:
    """説明文分析"""
    
    if not foods:
        return {"relevance_score": 0.0, "analysis": []}
    
    query_words = set(query.lower().split())
    target_words = set(target_food.lower().split()) if target_food else set()
    
    analysis = []
    relevance_scores = []
    
    for i, food in enumerate(foods[:5]):
        description = food.get("description", "").lower()
        desc_words = set(description.split())
        
        # 類似度計算
        query_similarity = SequenceMatcher(None, query.lower(), description).ratio()
        
        # キーワード一致度
        query_match = len(query_words.intersection(desc_words)) / len(query_words) if query_words else 0
        target_match = len(target_words.intersection(desc_words)) / len(target_words) if target_words else 0
        
        relevance = max(query_similarity, query_match, target_match)
        relevance_scores.append(relevance)
        
        analysis.append({
            "rank": i + 1,
            "description": food.get("description", ""),
            "relevance_score": relevance,
            "query_similarity": query_similarity,
            "keyword_match": query_match
        })
    
    return {
        "relevance_score": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0,
        "analysis": analysis
    }

def _analyze_nutrition_completeness(foods: List[Dict]) -> Dict[str, Any]:
    """栄養データ完全性分析"""
    
    if not foods:
        return {"score": 0.0, "analysis": []}
    
    essential_nutrients = [
        "Energy", "Protein", "Total lipid (fat)", "Carbohydrate, by difference",
        "Fiber, total dietary", "Sugars, total including NLEA", "Calcium, Ca",
        "Iron, Fe", "Sodium, Na", "Vitamin C, total ascorbic acid"
    ]
    
    completeness_scores = []
    analysis = []
    
    for food in foods[:5]:
        nutrients = food.get("foodNutrients", [])
        nutrient_names = [n.get("nutrientName", "") for n in nutrients]
        
        found_essential = sum(1 for essential in essential_nutrients
                            if any(essential in name for name in nutrient_names))
        
        completeness = found_essential / len(essential_nutrients)
        completeness_scores.append(completeness)
        
        analysis.append({
            "description": food.get("description", ""),
            "total_nutrients": len(nutrients),
            "essential_found": found_essential,
            "completeness_score": completeness
        })
    
    return {
        "score": sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0,
        "analysis": analysis
    }

def _analyze_top_results(foods: List[Dict], query: str) -> List[Dict]:
    """上位結果の詳細分析"""
    
    analysis = []
    
    for i, food in enumerate(foods):
        analysis.append({
            "rank": i + 1,
            "description": food.get("description", ""),
            "data_type": food.get("dataType", "Unknown"),
            "nutrient_count": len(food.get("foodNutrients", [])),
            "relevance_indicators": _get_relevance_indicators(food, query)
        })
    
    return analysis

def _get_relevance_indicators(food: Dict, query: str) -> List[str]:
    """関連性指標を取得"""
    
    indicators = []
    description = food.get("description", "").lower()
    query_lower = query.lower()
    
    # 直接一致
    if query_lower in description:
        indicators.append("exact_match")
    
    # 部分一致
    query_words = query_lower.split()
    if any(word in description for word in query_words):
        indicators.append("partial_match")
    
    # データタイプ
    data_type = food.get("dataType", "")
    if data_type in ["Foundation", "SR Legacy"]:
        indicators.append("high_quality_data")
    
    return indicators

def _analyze_data_types_enhanced(foods: List[Dict]) -> Dict[str, Any]:
    """拡張されたデータタイプ分析"""
    
    distribution = {}
    quality_analysis = {}
    
    for food in foods:
        data_type = food.get("dataType", "Unknown")
        distribution[data_type] = distribution.get(data_type, 0) + 1
    
    total = len(foods)
    
    # 品質分析
    quality_analysis = {
        "foundation_percentage": (distribution.get("Foundation", 0) / total * 100) if total > 0 else 0,
        "sr_legacy_percentage": (distribution.get("SR Legacy", 0) / total * 100) if total > 0 else 0,
        "branded_percentage": (distribution.get("Branded", 0) / total * 100) if total > 0 else 0,
        "quality_score": _calculate_data_type_quality_score(distribution, total)
    }
    
    return {
        "distribution": distribution,
        "quality_analysis": quality_analysis,
        "recommendations": _get_data_type_recommendations(quality_analysis)
    }

def _calculate_data_type_quality_score(distribution: Dict[str, int], total: int) -> float:
    """データタイプ品質スコア計算"""
    
    if total == 0:
        return 0.0
    
    weights = {
        "Foundation": 1.0,
        "SR Legacy": 0.8,
        "Survey (FNDDS)": 0.6,
        "Branded": 0.4
    }
    
    score = 0.0
    for data_type, count in distribution.items():
        weight = weights.get(data_type, 0.2)
        score += (count / total) * weight
    
    return score

def _get_data_type_recommendations(quality_analysis: Dict) -> List[str]:
    """データタイプに基づく推奨事項"""
    
    recommendations = []
    
    if quality_analysis["foundation_percentage"] < 20:
        recommendations.append("Foundation データの割合を増やすため、より具体的な検索語を使用してください")
    
    if quality_analysis["branded_percentage"] > 50:
        recommendations.append("ブランド商品が多すぎます。一般的な食材名での検索を試してください")
    
    if quality_analysis["quality_score"] < 0.6:
        recommendations.append("検索結果の品質が低いです。検索語を見直してください")
    
    return recommendations

def _calculate_relevance_score_enhanced(foods: List[Dict], query: str, target_food: Optional[str]) -> float:
    """拡張された関連性スコア計算"""
    
    if not foods:
        return 0.0
    
    scores = []
    query_lower = query.lower()
    target_lower = target_food.lower() if target_food else ""
    
    for food in foods[:10]:  # 上位10件を評価
        description = food.get("description", "").lower()
        
        # 複数の類似度指標を組み合わせ
        exact_match = 1.0 if query_lower in description else 0.0
        sequence_similarity = SequenceMatcher(None, query_lower, description).ratio()
        
        # キーワード一致度
        query_words = set(query_lower.split())
        desc_words = set(description.split())
        keyword_match = len(query_words.intersection(desc_words)) / len(query_words) if query_words else 0
        
        # ターゲット食材との一致度
        target_match = 0.0
        if target_lower:
            target_words = set(target_lower.split())
        target_match = len(target_words.intersection(desc_words)) / len(target_words) if target_words else 0
        
        # 総合スコア
        relevance = max(exact_match, sequence_similarity * 0.7, keyword_match * 0.8, target_match * 0.9)
        scores.append(relevance)
    
    return sum(scores) / len(scores) if scores else 0.0

def _calculate_completeness_score_enhanced(foods: List[Dict]) -> float:
    """拡張された完全性スコア計算"""
    
    if not foods:
        return 0.0
    
    # より包括的な栄養素リスト
    essential_nutrients = [
        "Energy", "Protein", "Total lipid (fat)", "Carbohydrate, by difference",
        "Fiber, total dietary", "Sugars, total including NLEA",
        "Calcium, Ca", "Iron, Fe", "Magnesium, Mg", "Phosphorus, P",
        "Potassium, K", "Sodium, Na", "Zinc, Zn",
        "Vitamin C, total ascorbic acid", "Thiamin", "Riboflavin",
        "Niacin", "Vitamin B-6", "Folate, total", "Vitamin B-12",
        "Vitamin A, RAE", "Vitamin E (alpha-tocopherol)", "Vitamin D (D2 + D3)",
        "Vitamin K (phylloquinone)"
    ]
    
    completeness_scores = []
    
    for food in foods[:5]:  # 上位5件を評価
        nutrients = food.get("foodNutrients", [])
        nutrient_names = [n.get("nutrientName", "") for n in nutrients]
        
        found_essential = sum(1 for essential in essential_nutrients
                            if any(essential in name for name in nutrient_names))
        
        completeness = found_essential / len(essential_nutrients)
        completeness_scores.append(completeness)
    
    return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0

def _calculate_diversity_score(foods: List[Dict]) -> float:
    """多様性スコア計算"""
    
    if not foods:
        return 0.0
    
    # データタイプの多様性
    data_types = set(food.get("dataType", "Unknown") for food in foods)
    data_type_diversity = len(data_types) / 4  # 最大4種類のデータタイプ
    
    # 説明文の多様性（類似度ベース）
    descriptions = [food.get("description", "") for food in foods[:10]]
    description_diversity = _calculate_description_diversity(descriptions)
    
    return (data_type_diversity + description_diversity) / 2

def _calculate_description_diversity(descriptions: List[str]) -> float:
    """説明文の多様性計算"""
    
    if len(descriptions) < 2:
        return 1.0
    
    similarities = []
    for i in range(len(descriptions)):
        for j in range(i + 1, len(descriptions)):
            similarity = SequenceMatcher(None, descriptions[i].lower(), descriptions[j].lower()).ratio()
            similarities.append(similarity)
    
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    return 1.0 - avg_similarity  # 類似度が低いほど多様性が高い

def _get_evaluation_weights(evaluation_focus: Optional[str]) -> Dict[str, float]:
    """評価フォーカスに応じた重み設定"""
    
    if evaluation_focus == "accuracy":
        return {
            "relevance": 0.5,
            "completeness": 0.2,
            "diversity": 0.1,
            "data_quality": 0.2
        }
    elif evaluation_focus == "completeness":
        return {
            "relevance": 0.2,
            "completeness": 0.5,
            "diversity": 0.1,
            "data_quality": 0.2
        }
    elif evaluation_focus == "relevance":
        return {
            "relevance": 0.6,
            "completeness": 0.1,
            "diversity": 0.1,
            "data_quality": 0.2
        }
    else:  # balanced
        return {
            "relevance": 0.3,
            "completeness": 0.3,
            "diversity": 0.2,
            "data_quality": 0.2
        }

def _generate_improvement_suggestions_enhanced(
    query: str, foods: List[Dict], total_hits: int, 
    evaluation: Dict, target_food: Optional[str]
) -> List[str]:
    """拡張された改善提案生成"""
    
    suggestions = []
    query_analysis = evaluation["query_analysis"]
    result_quality = evaluation["result_quality"]
    
    # クエリベースの提案
    if query_analysis["specificity_score"] < 0.5:
        suggestions.append("より具体的な検索語を使用してください（例：調理方法、部位、ブランド名）")
    
    if not query_analysis["modifiers"]["cooking_method"]:
        suggestions.append("調理状態を指定してください（例：raw, cooked, grilled）")
    
    if query_analysis["language"] == "japanese":
        suggestions.append("英語での検索も試してみてください（例：鶏肉 → chicken）")
    
    # 結果品質ベースの提案
    if result_quality["quality_score"] < 0.6:
        suggestions.append("検索結果の品質が低いです。より一般的な食材名を試してください")
    
    if len(foods) > 50:
        suggestions.append("結果が多すぎます。より具体的な条件を追加してください")
    elif len(foods) < 5:
        suggestions.append("結果が少なすぎます。より一般的な検索語を試してください")
    
    # データタイプベースの提案
    data_type_quality = result_quality.get("data_type_quality", {})
    if not data_type_quality.get("has_foundation", False):
        suggestions.append("Foundation データを含む結果を得るため、基本的な食材名を使用してください")
    
    # 多様性ベースの提案
    if evaluation["diversity_score"] < 0.3:
        suggestions.append("より多様な結果を得るため、検索語を調整してください")
    
    return suggestions

def _calculate_overall_score_enhanced(evaluation: Dict, weights: Dict[str, float]) -> float:
    """拡張された総合スコア計算"""
    
    scores = {
        "relevance": evaluation["relevance_score"],
        "completeness": evaluation["completeness_score"],
        "diversity": evaluation["diversity_score"],
        "data_quality": evaluation["result_quality"]["quality_score"]
    }
    
    weighted_score = sum(scores[key] * weights[key] for key in scores)
    return min(weighted_score, 1.0)

def _get_grade(score: float) -> str:
    """スコアからグレードを取得"""
    
    if score >= 0.9:
        return "A+"
    elif score >= 0.8:
        return "A"
    elif score >= 0.7:
        return "B+"
    elif score >= 0.6:
        return "B"
    elif score >= 0.5:
        return "C+"
    elif score >= 0.4:
        return "C"
    else:
        return "D"

def _get_assessment_summary_enhanced(score: float, result_count: int, total_hits: int) -> str:
    """拡張された評価サマリー"""

    grade = _get_grade(score)
    
    if score >= 0.8:
        quality = "優秀"
    elif score >= 0.6:
        quality = "良好"
    elif score >= 0.4:
        quality = "普通"
    else:
        quality = "改善が必要"
    
    return f"検索品質: {quality} (グレード: {grade}, スコア: {score:.2f}), 結果数: {result_count}/{total_hits}"

def _generate_detailed_analysis(evaluation: Dict, foods: List[Dict]) -> Dict[str, Any]:
    """詳細分析生成"""
    
    return {
        "query_insights": _get_query_insights(evaluation["query_analysis"]),
        "result_insights": _get_result_insights(evaluation["result_quality"]),
        "performance_metrics": _get_performance_metrics(evaluation),
        "comparison_baseline": _get_baseline_comparison(evaluation)
    }

def _get_query_insights(query_analysis: Dict) -> Dict[str, Any]:
    """クエリ洞察"""
    
    insights = {
        "strengths": [],
        "weaknesses": [],
        "optimization_potential": []
    }
    
    # 強み
    if query_analysis["specificity_score"] > 0.7:
        insights["strengths"].append("高い具体性")
    
    if query_analysis["detected_categories"]:
        insights["strengths"].append(f"明確な食材カテゴリ: {', '.join(query_analysis['detected_categories'])}")
    
    # 弱み
    if query_analysis["complexity_level"] == "simple" and query_analysis["specificity_score"] < 0.5:
        insights["weaknesses"].append("シンプルすぎるクエリ")
    
    if query_analysis["potential_issues"]:
        insights["weaknesses"].extend(query_analysis["potential_issues"])
    
    # 最適化の可能性
    if not query_analysis["modifiers"]["cooking_method"]:
        insights["optimization_potential"].append("調理方法の追加")
    
    if not query_analysis["modifiers"]["part"]:
        insights["optimization_potential"].append("部位の指定")
    
    return insights

def _get_result_insights(result_quality: Dict) -> Dict[str, Any]:
    """結果洞察"""
    
    insights = {
        "data_quality_assessment": "高品質" if result_quality["quality_score"] > 0.7 else "改善の余地あり",
        "top_result_analysis": result_quality.get("top_results_analysis", []),
        "data_source_distribution": result_quality.get("data_type_quality", {}).get("distribution", {}),
        "nutrition_coverage": result_quality.get("nutrition_completeness", {}).get("score", 0.0)
    }
    
    return insights

def _get_performance_metrics(evaluation: Dict) -> Dict[str, float]:
    """パフォーマンス指標"""
    
    return {
        "relevance_score": evaluation["relevance_score"],
        "completeness_score": evaluation["completeness_score"],
        "diversity_score": evaluation["diversity_score"],
        "overall_score": evaluation["overall_assessment"]["score"]
    }

def _get_baseline_comparison(evaluation: Dict) -> Dict[str, str]:
    """ベースライン比較"""
    
    score = evaluation["overall_assessment"]["score"]
    
    return {
        "vs_average": "上回る" if score > 0.6 else "下回る",
        "vs_good_practice": "達成" if score > 0.7 else "未達成",
        "improvement_needed": "はい" if score < 0.6 else "いいえ"
    }

def _get_recommendations_enhanced(evaluation: Dict) -> List[str]:
    """拡張された推奨事項"""
    
    recommendations = []
    score = evaluation["overall_assessment"]["score"]
    
    if score < 0.6:
        recommendations.append("検索戦略の根本的な見直しが必要です")
        recommendations.append("より基本的な食材名から始めることをお勧めします")
    
    if evaluation["diversity_score"] < 0.3:
        recommendations.append("検索語のバリエーションを増やしてください")
    
    if evaluation["completeness_score"] < 0.5:
        recommendations.append("Foundation または SR Legacy データを優先してください")
    
    recommendations.extend(evaluation["improvement_suggestions"])
    
    return list(set(recommendations))  # 重複を除去

def _suggest_next_steps(evaluation: Dict, query: str) -> List[str]:
    """次のステップ提案"""
    
    steps = []
    score = evaluation["overall_assessment"]["score"]
    query_analysis = evaluation["query_analysis"]
    
    if score < 0.5:
        steps.append("1. 検索語を簡素化して基本的な食材名のみで再検索")
        steps.append("2. 英語での検索を試行")
        steps.append("3. 類似食材での検索を検討")
    elif score < 0.7:
        steps.append("1. 修飾語（調理方法、部位）を追加")
        steps.append("2. より具体的な検索条件を設定")
    else:
        steps.append("1. 現在の検索戦略を維持")
        steps.append("2. 必要に応じて結果を絞り込み")
    
    # 言語固有の提案
    if query_analysis["language"] == "japanese":
        steps.append("4. 英語翻訳版での検索も実行")
    
    return steps