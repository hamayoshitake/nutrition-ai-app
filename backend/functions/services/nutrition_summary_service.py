"""
栄養サマリー取得用ビジネスロジックを提供するサービスモジュール
"""

from typing import Any, Dict


class NutritionSummaryService:
    """
    USDA FoodData Central 詳細APIのレスポンスから主要栄養素サマリーを生成するサービスクラス
    """

    def summarize(self, food_data: Dict[str, Any]) -> Dict[str, float]:
        """
        食品データから主要栄養素を抽出し、辞書で返却します。

        Args:
            food_data: USDA 詳細API のレスポンスJSON

        Returns:
            栄養素サマリーの辞書
        """
        # 初期化
        summary: Dict[str, Any] = {
            "description": food_data.get("description", "不明な食品")
        }

        # 1. labelNutrients からデータを取得
        label = food_data.get("labelNutrients", {}) or {}
        if label:
            if "protein" in label and "value" in label["protein"]:
                summary["protein_g"] = round(label["protein"]["value"], 2)
            if "fat" in label and "value" in label["fat"]:
                summary["fat_g"] = round(label["fat"]["value"], 2)
            if "carbohydrates" in label and "value" in label["carbohydrates"]:
                summary["carbohydrates_g"] = round(label["carbohydrates"]["value"], 2)
            if "fiber" in label and "value" in label["fiber"]:
                summary["fiber_g"] = round(label["fiber"]["value"], 2)
            if "sugars" in label and "value" in label["sugars"]:
                summary["sugars_g"] = round(label["sugars"]["value"], 2)
            if "calories" in label and "value" in label["calories"]:
                summary["energy_kcal"] = round(label["calories"]["value"], 2)
            if "iron" in label and "value" in label["iron"]:
                summary["iron_mg"] = round(label["iron"]["value"], 2)
            if "calcium" in label and "value" in label["calcium"]:
                summary["calcium_mg"] = round(label["calcium"]["value"], 2)
            if "sodium" in label and "value" in label["sodium"]:
                summary["sodium_mg"] = round(label["sodium"]["value"], 2)

        # 2. foodNutrients からデータを取得
        nutrients = food_data.get("foodNutrients", []) or []
        nutrients_dict: Dict[str, float] = {}
        for item in nutrients:
            if "nutrient" in item and "name" in item["nutrient"]:
                name = item["nutrient"]["name"]
                amount = item.get("amount", 0)
                nutrients_dict[name] = amount

        # 主要な栄養素を抽出
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

        # サービングサイズがあれば per_serving を計算
        serving_size = food_data.get("servingSize")
        serving_unit = food_data.get("servingSizeUnit")
        if serving_size and serving_unit == "g":
            factor = serving_size / 100.0
            for k, v in list(summary.items()):
                if isinstance(v, (int, float)) and k != "description":
                    summary[f"{k}_per_serving"] = round(v * factor, 2)

        return summary 