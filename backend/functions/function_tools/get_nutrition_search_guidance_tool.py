from agents import function_tool
from typing import Any, Dict, List, Optional
import re

def get_nutrition_search_guidance_core(
    food_category: Optional[str] = None,
    search_intent: Optional[str] = None,
    user_input: Optional[str] = None
) -> Dict[str, Any]:
    """
    栄養データ検索のベストプラクティスとガイダンスを提供します（コア関数）。
    非決定論的なユーザー入力に対応した包括的なガイダンスを提供。

    Args:
        food_category: 食材カテゴリ
        search_intent: 検索の意図
        user_input: ユーザーの実際の入力（分析用）

    Returns:
        検索ガイダンス情報を含む辞書
    """
    
    guidance = {
        "general_tips": _get_general_tips(),
        "data_type_guidance": _get_data_type_guidance(),
        "recommended_data_types": ["Foundation", "SR Legacy"],
        "translation_patterns": _get_translation_patterns(),
        "fallback_strategies": _get_fallback_strategies()
    }
    
    # ユーザー入力の分析と具体的な提案
    if user_input:
        input_analysis = _analyze_user_input(user_input)
        guidance["input_analysis"] = input_analysis
        guidance["specific_suggestions"] = _get_specific_suggestions(user_input)
    
    # カテゴリ別ガイダンス（拡張版）
    if food_category:
        category_guidance = _get_enhanced_category_guidance(food_category.lower())
        guidance["category_specific"] = category_guidance
    
    # 検索意図別ガイダンス
    if search_intent:
        intent_guidance = _get_intent_specific_guidance(search_intent.lower())
        guidance["intent_specific"] = intent_guidance
    
    # 包括的な検索例
    guidance["comprehensive_examples"] = _get_comprehensive_examples()
    
    return {
        "status": "success",
        "guidance": guidance,
        "usage_tips": _get_enhanced_usage_tips()
    }

@function_tool(strict_mode=False)
def get_nutrition_search_guidance_tool(
    food_category: Optional[str] = None,
    search_intent: Optional[str] = None,
    user_input: Optional[str] = None
) -> Dict[str, Any]:
    """
    栄養データ検索のベストプラクティスとガイダンスを提供します。
    非決定論的なユーザー入力に対応した包括的なガイダンスを提供。

    Args:
        food_category: 食材カテゴリ
        search_intent: 検索の意図
        user_input: ユーザーの実際の入力（分析用）

    Returns:
        検索ガイダンス情報を含む辞書
    """
    return get_nutrition_search_guidance_core(food_category, search_intent, user_input)

def _get_general_tips() -> Dict[str, List[str]]:
    """拡張された一般的な検索ガイダンス"""
    return {
        "effective_keywords": [
            "英語での食材名を使用する（日本語→英語変換を活用）",
            "具体的な部位や調理法を含める",
            "ブランド名よりも一般的な食材名を優先",
            "複数の類似語を試す（例：eggplant, aubergine）",
            "地域差のある名称に注意（US vs UK English）"
        ],
        "search_strategies": [
            "基本的な食材名で開始",
            "結果が多すぎる場合は修飾語を追加",
            "結果が少ない場合は上位概念や類似語を試行",
            "複合食材は主要成分に分解",
            "加工度の低い基本食材を優先"
        ],
        "common_pitfalls": [
            "過度に具体的な検索（例：特定ブランド名）",
            "曖昧すぎる検索（例：「野菜」「肉」のみ）",
            "調理状態の混同（raw vs cooked）",
            "部位の未指定（肉類の場合）"
        ]
    }

def _get_data_type_guidance() -> Dict[str, str]:
    """データタイプガイダンス"""
    return {
        "Foundation": "最も信頼性の高い基本的な食材データ",
        "SR Legacy": "従来のUSDA標準参照データベース",
        "Branded": "ブランド商品データ（特定商品の場合のみ使用）",
        "Survey": "調査データ（一般的な検索では推奨しない）"
    }

def _get_translation_patterns() -> Dict[str, Dict[str, str]]:
    """日本語→英語翻訳パターン（拡張版）"""
    return {
        "basic_foods": {
            # 基本食材
            "りんご": "apple", "バナナ": "banana", "オレンジ": "orange",
            "鶏肉": "chicken", "牛肉": "beef", "豚肉": "pork",
            "米": "rice", "パン": "bread", "卵": "egg",
            "牛乳": "milk", "チーズ": "cheese",
            
            # 野菜類
            "キャベツ": "cabbage", "レタス": "lettuce", "トマト": "tomato",
            "玉ねぎ": "onion", "人参": "carrot", "じゃがいも": "potato",
            "ブロッコリー": "broccoli", "ほうれん草": "spinach",
            
            # 魚介類
            "鮭": "salmon", "まぐろ": "tuna", "鯛": "sea bream",
            "えび": "shrimp", "いか": "squid", "たこ": "octopus",
            
            # 豆・ナッツ類
            "大豆": "soybean", "小豆": "adzuki bean", "アーモンド": "almond",
            "くるみ": "walnut", "ピーナッツ": "peanut",
            
            # アジア系食材
            "納豆": "natto fermented soybeans",
            "味噌": "miso soybean paste",
            "昆布": "kelp seaweed",
            "わかめ": "wakame seaweed",
            "こんにゃく": "konjac",
            "豆腐": "tofu"
        },
        "cooking_methods": {
            "生": "raw", "茹でた": "boiled", "焼いた": "grilled",
            "蒸した": "steamed", "揚げた": "fried", "炒めた": "stir-fried",
            "煮た": "simmered", "炙った": "broiled"
        },
        "parts_cuts": {
            "胸肉": "breast", "もも肉": "thigh", "手羽": "wing",
            "ひき肉": "ground", "骨なし": "boneless", "皮なし": "skinless"
        }
    }

def _analyze_user_input(user_input: str) -> Dict[str, Any]:
    """ユーザー入力の分析"""
    analysis = {
        "detected_language": "japanese" if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', user_input) else "english",
        "input_type": _classify_input_type(user_input),
        "complexity": _assess_complexity(user_input),
        "potential_issues": _identify_potential_issues(user_input),
        "word_count": len(user_input.split()),
        "detected_food": _detect_food_items(user_input),
        "has_modifiers": _has_modifiers(user_input)
    }
    return analysis

def _classify_input_type(user_input: str) -> str:
    """入力タイプの分類"""
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in ["サラダ", "salad", "カレー", "curry"]):
        return "composite_dish"
    elif any(word in input_lower for word in ["ジュース", "juice", "スープ", "soup"]):
        return "processed_food"
    elif len(input_lower.split()) == 1:
        return "simple_ingredient"
    else:
        return "complex_ingredient"

def _assess_complexity(user_input: str) -> str:
    """入力の複雑さを評価"""
    word_count = len(user_input.split())
    if word_count == 1:
        return "simple"
    elif word_count <= 3:
        return "moderate"
    else:
        return "complex"

def _detect_food_items(user_input: str) -> List[str]:
    """食材の検出"""
    detected = []
    translation_patterns = _get_translation_patterns()
    
    for jp, en in translation_patterns["basic_foods"].items():
        if jp in user_input or en in user_input.lower():
            detected.append(en)
    
    return detected

def _has_modifiers(user_input: str) -> bool:
    """修飾語の有無を確認"""
    modifiers = ["raw", "cooked", "fresh", "skinless", "boneless", "生", "茹でた", "焼いた"]
    return any(mod in user_input.lower() for mod in modifiers)

def _identify_potential_issues(user_input: str) -> List[str]:
    """潜在的な問題を特定"""
    issues = []
    input_lower = user_input.lower()
    
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', user_input):
        issues.append("japanese_input_needs_translation")
    
    if any(brand in input_lower for brand in ["コカコーラ", "coca-cola", "マクドナルド", "mcdonald"]):
        issues.append("brand_specific_input")
    
    if any(vague in input_lower for vague in ["野菜", "vegetable", "肉", "meat", "魚", "fish"]):
        issues.append("too_vague")
    
    if "サラダ" in user_input or "salad" in input_lower:
        issues.append("composite_dish")
        
    return issues

def _get_specific_suggestions(user_input: str) -> List[str]:
    """ユーザー入力に対する具体的な提案"""
    suggestions = []
    input_lower = user_input.lower()
    
    # 日本語入力の場合
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', user_input):
        translation_patterns = _get_translation_patterns()
        for jp, en in translation_patterns["basic_foods"].items():
            if jp in user_input:
                suggestions.append(f"'{jp}' → '{en}' として検索してください")
    
    # 複合料理の場合
    if any(dish in input_lower for dish in ["salad", "curry", "soup", "sandwich"]):
        suggestions.append("複合料理は主要な材料に分解して個別に検索することを推奨します")
        suggestions.append("例：チキンサラダ → chicken breast, lettuce, tomato として個別検索")
    
    # 曖昧な入力の場合
    if input_lower in ["meat", "vegetable", "fruit", "肉", "野菜", "果物"]:
        suggestions.append("より具体的な食材名を指定してください")
        suggestions.append("例：'meat' → 'chicken breast', 'beef ground', 'pork chop'")
    
    return suggestions

def _get_enhanced_category_guidance(category: str) -> Dict[str, Any]:
    """拡張されたカテゴリ別ガイダンス"""
    
    enhanced_categories = {
        "meat": {
            "subcategories": ["poultry", "beef", "pork", "lamb", "game"],
            "keywords": ["chicken", "beef", "pork", "turkey", "duck", "lamb"],
            "modifiers": ["breast", "thigh", "ground", "lean", "skinless", "boneless", "raw", "cooked"],
            "examples": [
                "chicken breast skinless boneless raw",
                "beef ground 85% lean raw",
                "pork chop boneless cooked"
            ],
            "tips": [
                "部位を明確に指定する（breast, thigh, etc.）",
                "皮の有無を指定する（skinless/with skin）",
                "調理状態を指定する（raw/cooked）",
                "脂肪含有量を考慮する（lean, 85% lean, etc.）"
            ]
        },
        "seafood": {
            "subcategories": ["fish", "shellfish", "mollusks"],
            "keywords": ["salmon", "tuna", "cod", "shrimp", "crab", "oyster"],
            "modifiers": ["fresh", "frozen", "raw", "cooked", "farmed", "wild"],
            "examples": [
                "salmon atlantic farmed raw",
                "tuna yellowfin fresh raw",
                "shrimp cooked moist heat"
            ],
            "tips": [
                "魚種を具体的に指定する",
                "養殖か天然かを明確にする",
                "調理状態を指定する"
            ]
        },
        "nuts_seeds": {
            "subcategories": ["tree_nuts", "seeds", "legumes"],
            "keywords": ["almond", "walnut", "peanut", "sunflower seed", "chia seed"],
            "modifiers": ["raw", "roasted", "salted", "unsalted", "whole", "chopped"],
            "examples": [
                "almonds raw",
                "walnuts english raw",
                "sunflower seeds dry roasted"
            ],
            "tips": [
                "加工状態を明確にする（raw/roasted）",
                "塩分の有無を指定する"
            ]
        },
        "beverages": {
            "subcategories": ["juices", "dairy_drinks", "plant_milks", "alcoholic"],
            "keywords": ["orange juice", "milk", "almond milk", "coffee", "tea"],
            "modifiers": ["fresh", "from concentrate", "unsweetened", "whole", "skim"],
            "examples": [
                "orange juice fresh",
                "milk whole 3.25% milkfat",
                "almond milk unsweetened"
            ],
            "tips": [
                "濃縮か生搾りかを明確にする",
                "糖分添加の有無を確認する"
            ]
        },
        "oils_fats": {
            "subcategories": ["cooking_oils", "butter", "margarine"],
            "keywords": ["olive oil", "coconut oil", "butter", "margarine"],
            "modifiers": ["extra virgin", "refined", "salted", "unsalted"],
            "examples": [
                "olive oil extra virgin",
                "coconut oil raw",
                "butter salted"
            ],
            "tips": [
                "精製度を指定する",
                "塩分の有無を明確にする"
            ]
        },
        "fruit": {
            "keywords": ["apple", "banana", "orange", "strawberry", "grape", "mango", "pineapple"],
            "modifiers": ["fresh", "raw", "without skin", "with skin", "frozen"],
            "examples": [
                "apple raw with skin",
                "banana raw",
                "strawberries raw"
            ],
            "tips": [
                "新鮮な状態（fresh, raw）を指定する",
                "皮の有無を明確にする",
                "品種が重要な場合は指定する"
            ]
        },
        "vegetable": {
            "subcategories": ["leafy_greens", "root_vegetables", "cruciferous", "nightshades"],
            "keywords": ["broccoli", "carrot", "spinach", "tomato", "potato", "onion", "bell pepper"],
            "modifiers": ["raw", "cooked", "boiled", "steamed", "roasted", "without salt"],
            "examples": [
                "broccoli raw",
                "carrot raw",
                "spinach raw"
            ],
            "tips": [
                "調理方法を指定する（raw/cooked）",
                "塩分添加の有無を考慮する"
            ]
        },
        "dairy": {
            "keywords": ["milk", "cheese", "yogurt", "butter", "cream"],
            "modifiers": ["whole", "2%", "skim", "low fat", "plain", "greek"],
            "examples": [
                "milk whole 3.25% milkfat",
                "yogurt plain whole milk",
                "cheese cheddar"
            ],
            "tips": [
                "脂肪含有量を指定する",
                "プレーンか味付きかを明確にする"
            ]
        },
        "grain": {
            "subcategories": ["cereals", "pasta", "bread", "rice"],
            "keywords": ["rice", "bread", "pasta", "oats", "quinoa", "wheat", "barley"],
            "modifiers": ["white", "brown", "whole grain", "enriched", "cooked", "dry"],
            "examples": [
                "rice white long-grain cooked",
                "bread whole wheat",
                "oats dry"
            ],
            "tips": [
                "精製度を指定する（white/brown/whole grain）",
                "調理状態を指定する（cooked/dry）"
            ]
        }
    }
    
    return enhanced_categories.get(category, {
        "tips": ["一般的な食材名を使用してください", "英語での検索を推奨します"],
        "fallback_strategy": "基本的な食材名で検索し、必要に応じて修飾語を追加してください"
    })

def _get_intent_specific_guidance(intent: str) -> Dict[str, Any]:
    """検索意図別のガイダンスを返す"""
    
    intent_guides = {
        "basic_nutrition": {
            "recommended_data_types": ["Foundation", "SR Legacy"],
            "focus": "基本的な栄養素（カロリー、タンパク質、脂質、炭水化物）",
            "tips": [
                "Foundation データタイプを最優先する",
                "一般的な食材名で検索する",
                "調理状態を明確にする"
            ]
        },
        "detailed_analysis": {
            "recommended_data_types": ["Foundation"],
            "focus": "詳細な栄養素分析（ビタミン、ミネラル、アミノ酸）",
            "tips": [
                "Foundation データタイプのみを使用する",
                "具体的な品種や部位を指定する",
                "複数の類似食材を比較検討する"
            ]
        },
        "comparison": {
            "recommended_data_types": ["Foundation", "SR Legacy"],
            "focus": "複数食材の栄養価比較",
            "tips": [
                "同じデータタイプで統一する",
                "同じ調理状態で比較する",
                "100gあたりの値で正規化する"
            ]
        },
        "high_protein": {
            "recommended_data_types": ["Foundation", "SR Legacy"],
            "focus": "高タンパク質食材の特定",
            "tips": [
                "肉類、魚類、豆類を優先的に検索",
                "タンパク質含有量でソート",
                "調理による変化を考慮"
            ]
        },
        "low_carb": {
            "recommended_data_types": ["Foundation", "SR Legacy"],
            "focus": "低炭水化物食材の特定",
            "tips": [
                "野菜類、肉類、魚類を中心に検索",
                "炭水化物含有量を確認",
                "糖質と食物繊維を区別"
            ]
        }
    }
    
    return intent_guides.get(intent, {
        "tips": ["検索の目的を明確にしてください"]
    })

def _get_fallback_strategies() -> Dict[str, List[str]]:
    """フォールバック戦略"""
    return {
        "no_results": [
            "より一般的な用語を使用する（例：'chicken breast' → 'chicken'）",
            "類似語を試す（例：'eggplant' → 'aubergine'）",
            "上位概念を使用する（例：'salmon' → 'fish'）",
            "データタイプを変更する（Foundation → SR Legacy → Branded）"
        ],
        "too_many_results": [
            "より具体的な修飾語を追加する",
            "調理状態を明確にする（raw/cooked）",
            "部位を指定する（肉類の場合）",
            "データタイプを限定する（Foundationのみ）"
        ],
        "unknown_food": [
            "類似の知られた食材で代替する",
            "主要成分に分解する",
            "地域名から一般名に変換する",
            "英語の別表現を試す"
        ],
        "api_errors": [
            "ネットワーク接続を確認する",
            "API制限に達していないか確認する",
            "より簡単なクエリで再試行する",
            "キャッシュされた結果を使用する"
        ]
    }

def _get_comprehensive_examples() -> Dict[str, Any]:
    """包括的な検索例"""
    return {
        "excellent_queries_by_category": {
            "meat": [
                "chicken breast skinless boneless raw",
                "beef ground 85% lean raw",
                "pork chop bone-in cooked"
            ],
            "seafood": [
                "salmon atlantic farmed raw",
                "shrimp cooked moist heat",
                "tuna yellowfin fresh raw"
            ],
            "vegetables": [
                "broccoli raw",
                "carrot raw",
                "spinach raw"
            ],
            "fruits": [
                "apple raw with skin",
                "banana raw",
                "orange raw all commercial varieties"
            ],
            "grains": [
                "rice white long-grain cooked",
                "bread whole wheat",
                "oats dry"
            ],
            "dairy": [
                "milk whole 3.25% milkfat",
                "cheese cheddar",
                "yogurt plain whole milk"
            ],
            "nuts_seeds": [
                "almonds raw",
                "walnuts english raw",
                "sunflower seeds dry roasted"
            ]
        },
        "problematic_inputs_and_solutions": {
            "野菜サラダ": {
                "issue": "複合料理 + 日本語",
                "solution": "lettuce raw, tomato raw, carrot raw として個別検索"
            },
            "チキンカレー": {
                "issue": "複合料理 + 日本語",
                "solution": "chicken breast cooked, rice white cooked として個別検索"
            },
            "コカコーラ": {
                "issue": "ブランド名",
                "solution": "cola carbonated として検索"
            }
        },
        "excellent_queries": [
            "chicken breast skinless boneless raw",
            "apple raw with skin",
            "rice white long-grain cooked",
            "salmon atlantic farmed raw",
            "broccoli raw"
        ],
        "good_queries": [
            "chicken breast",
            "apple fresh",
            "white rice cooked",
            "salmon raw",
            "broccoli"
        ],
        "poor_queries": [
            "chicken",  # 部位が不明確
            "apple juice",  # 加工品（生の果物と栄養価が大きく異なる）
            "rice",  # 種類・調理状態が不明確
            "fish",  # 種類が不明確
            "vegetable"  # 具体性に欠ける
        ]
    }

def _get_enhanced_usage_tips() -> List[str]:
    """拡張された使用方法のヒント"""
    return [
        "🔤 日本語入力の場合は必ず英語に翻訳してから検索",
        "🎯 複合料理は主要材料に分解して個別検索",
        "📊 Foundation または SR Legacy データタイプを優先",
        "🔍 結果が見つからない場合は類似語や上位概念を試行",
        "⚖️ 調理状態（raw/cooked）を必ず明確にする",
        "🥩 肉類は部位と皮の有無を指定する",
        "🌟 ブランド名ではなく一般的な食材名を使用",
        "🎨 複数の検索パターンを試して最適な結果を見つける"
    ]