#!/usr/bin/env python3
# test_nutrition_summary_service.py

import os
import sys
import pytest

# backend/functions 直下をモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.nutrition_summary_service import NutritionSummaryService

class TestNutritionSummaryService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = NutritionSummaryService()

    def test_label_nutrients_only(self):
        food_data = {
            "description": "Test Food",
            "labelNutrients": {
                "protein": {"value": 10.123},
                "fat": {"value": 5.456},
                "carbohydrates": {"value": 20.789},
                "fiber": {"value": 1.234},
                "sugars": {"value": 2.345},
                "calories": {"value": 100.567},
                "iron": {"value": 0.12},
                "calcium": {"value": 0.34},
                "sodium": {"value": 0.56},
            }
        }
        result = self.service.summarize(food_data)
        assert result["description"] == "Test Food"
        assert result["protein_g"] == round(10.123, 2)
        assert result["fat_g"] == round(5.456, 2)
        assert result["carbohydrates_g"] == round(20.789, 2)
        assert result["fiber_g"] == round(1.234, 2)
        assert result["sugars_g"] == round(2.345, 2)
        assert result["energy_kcal"] == round(100.567, 2)
        assert result["iron_mg"] == round(0.12, 2)
        assert result["calcium_mg"] == round(0.34, 2)
        assert result["sodium_mg"] == round(0.56, 2)
        # per_serving は存在しない
        assert not any(k.endswith("_per_serving") for k in result.keys())

    def test_food_nutrients_only(self):
        food_data = {
            "description": "Test Food 2",
            "foodNutrients": [
                {"nutrient": {"name": "Protein"}, "amount": 8.1},
                {"nutrient": {"name": "Total lipid (fat)"}, "amount": 2.2},
                {"nutrient": {"name": "Carbohydrate, by difference"}, "amount": 15.3},
                {"nutrient": {"name": "Energy"}, "amount": 80.4},
                {"nutrient": {"name": "Fiber, total dietary"}, "amount": 3.3},
                {"nutrient": {"name": "Sugars, total including NLEA"}, "amount": 1.1},
                {"nutrient": {"name": "Vitamin C, total ascorbic acid"}, "amount": 0.01},
            ]
        }
        result = self.service.summarize(food_data)
        assert result["description"] == "Test Food 2"
        assert result["protein_g"] == round(8.1, 2)
        assert result["fat_g"] == round(2.2, 2)
        assert result["carbohydrates_g"] == round(15.3, 2)
        assert result["fiber_g"] == round(3.3, 2)
        assert result["sugars_g"] == round(1.1, 2)
        assert result["energy_kcal"] == round(80.4, 2)
        assert result["vitamin_c_mg"] == round(0.01, 2)
        assert not any(k.endswith("_per_serving") for k in result.keys())

    def test_serving_size_per_serving(self):
        food_data = {
            "description": "Test Food 3",
            "labelNutrients": {"protein": {"value": 5}, "calories": {"value": 200}},
            "servingSize": 50,
            "servingSizeUnit": "g"
        }
        result = self.service.summarize(food_data)
        assert result["protein_g"] == round(5, 2)
        assert result["energy_kcal"] == round(200, 2)
        # factor = 50/100 = 0.5
        assert result["protein_g_per_serving"] == round(5 * 0.5, 2)
        assert result["energy_kcal_per_serving"] == round(200 * 0.5, 2)

    def test_no_nutrients(self):
        food_data = {"description": "Unknown Food"}
        result = self.service.summarize(food_data)
        assert result == {"description": "Unknown Food"}

    def test_default_description(self):
        result = self.service.summarize({})
        assert result["description"] == "不明な食品"