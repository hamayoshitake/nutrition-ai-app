"""
栄養サマリー取得用ビジネスロジックを提供するサービスモジュール
"""

from typing import Any, Dict


class NutritionSummaryService:
    """
    USDA FoodData Central 詳細APIのレスポンスから主要栄養素サマリーを生成するサービスクラス
    全ての栄養価を100gあたりに正規化して返却します。
    """

    def summarize(self, food_data: Dict[str, Any]) -> Dict[str, float]:
        """
        食品データから主要栄養素を抽出し、100gあたりに正規化して辞書で返却します。

        Args:
            food_data: USDA 詳細API のレスポンスJSON

        Returns:
            100gあたりの栄養素サマリーの辞書
        """
        # 初期化
        summary: Dict[str, Any] = {
            "description": food_data.get("description", "不明な食品"),
            "note": "100gあたりの栄養価"
        }

        # データソースの重量を確認（100gベースかどうか）
        serving_size = food_data.get("servingSize")
        serving_unit = food_data.get("servingSizeUnit", "").lower()
        
        # 100gあたりへの変換係数を計算
        conversion_factor = 1.0  # デフォルトは100gベース
        
        if serving_size and serving_unit == "g":
            # サービングサイズがグラム単位の場合
            conversion_factor = 100.0 / serving_size
            print(f"🔧 変換係数: {serving_size}g → 100g (係数: {conversion_factor:.3f})")
        else:
            print(f"🔧 100gベースデータとして処理")

        # 1. labelNutrients からデータを取得（優先）
        label = food_data.get("labelNutrients", {}) or {}
        if label:
            if "protein" in label and "value" in label["protein"]:
                summary["protein_g"] = round(label["protein"]["value"] * conversion_factor, 2)
            if "fat" in label and "value" in label["fat"]:
                summary["fat_g"] = round(label["fat"]["value"] * conversion_factor, 2)
            if "carbohydrates" in label and "value" in label["carbohydrates"]:
                summary["carbohydrates_g"] = round(label["carbohydrates"]["value"] * conversion_factor, 2)
            if "fiber" in label and "value" in label["fiber"]:
                summary["fiber_g"] = round(label["fiber"]["value"] * conversion_factor, 2)
            if "sugars" in label and "value" in label["sugars"]:
                summary["sugars_g"] = round(label["sugars"]["value"] * conversion_factor, 2)
            if "calories" in label and "value" in label["calories"]:
                summary["energy_kcal"] = round(label["calories"]["value"] * conversion_factor, 2)
            if "iron" in label and "value" in label["iron"]:
                summary["iron_mg"] = round(label["iron"]["value"] * conversion_factor, 2)
            if "calcium" in label and "value" in label["calcium"]:
                summary["calcium_mg"] = round(label["calcium"]["value"] * conversion_factor, 2)
            if "sodium" in label and "value" in label["sodium"]:
                summary["sodium_mg"] = round(label["sodium"]["value"] * conversion_factor, 2)

        # 2. foodNutrients からデータを取得（補完用）
        nutrients = food_data.get("foodNutrients", []) or []
        nutrients_dict: Dict[str, float] = {}
        for item in nutrients:
            if "nutrient" in item and "name" in item["nutrient"]:
                name = item["nutrient"]["name"]
                amount = item.get("amount", 0)
                # 100gあたりに正規化
                nutrients_dict[name] = amount * conversion_factor

        # 主要な栄養素を抽出（labelNutrientsで取得できなかった場合の補完）
        if "Protein" in nutrients_dict and "protein_g" not in summary:
            summary["protein_g"] = round(nutrients_dict["Protein"], 2)
        if "Total lipid (fat)" in nutrients_dict and "fat_g" not in summary:
            summary["fat_g"] = round(nutrients_dict["Total lipid (fat)"], 2)
        if "Carbohydrate, by difference" in nutrients_dict and "carbohydrates_g" not in summary:
            summary["carbohydrates_g"] = round(nutrients_dict["Carbohydrate, by difference"], 2)
        if "Energy" in nutrients_dict and "energy_kcal" not in summary:
            summary["energy_kcal"] = round(nutrients_dict["Energy"], 2)
        if "Fiber, total dietary" in nutrients_dict and "fiber_g" not in summary:
            summary["fiber_g"] = round(nutrients_dict["Fiber, total dietary"], 2)
        if "Sugars, total including NLEA" in nutrients_dict and "sugars_g" not in summary:
            summary["sugars_g"] = round(nutrients_dict["Sugars, total including NLEA"], 2)
        if "Vitamin C, total ascorbic acid" in nutrients_dict:
            summary["vitamin_c_mg"] = round(nutrients_dict["Vitamin C, total ascorbic acid"], 2)

        # 追加のミネラル・ビタミン
        if "Iron, Fe" in nutrients_dict and "iron_mg" not in summary:
            summary["iron_mg"] = round(nutrients_dict["Iron, Fe"], 2)
        if "Calcium, Ca" in nutrients_dict and "calcium_mg" not in summary:
            summary["calcium_mg"] = round(nutrients_dict["Calcium, Ca"], 2)
        if "Sodium, Na" in nutrients_dict and "sodium_mg" not in summary:
            summary["sodium_mg"] = round(nutrients_dict["Sodium, Na"], 2)
        if "Potassium, K" in nutrients_dict:
            summary["potassium_mg"] = round(nutrients_dict["Potassium, K"], 2)
        if "Magnesium, Mg" in nutrients_dict:
            summary["magnesium_mg"] = round(nutrients_dict["Magnesium, Mg"], 2)

        # デバッグ情報を追加
        summary["serving_info"] = {
            "original_serving_size": serving_size,
            "original_serving_unit": serving_unit,
            "conversion_factor": round(conversion_factor, 3),
            "normalized_to": "100g"
        }

        print(f"📊 100gあたり栄養価計算完了: エネルギー={summary.get('energy_kcal', 'N/A')}kcal")
        
        return summary