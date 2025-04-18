from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import openai

app = FastAPI(title="Nutrition AI API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FoodItem(BaseModel):
    name: str
    quantity: float
    unit: str
    meal_time: datetime

class NutritionAnalysis(BaseModel):
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    recommendations: List[str]

@app.post("/api/analyze-meal", response_model=NutritionAnalysis)
async def analyze_meal(food_items: List[FoodItem]):
    try:
        # 食事内容の分析
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        # ここで食品データベースを参照してカロリーと栄養素を計算
        
        # AIによる食事アドバイスの生成
        recommendations = [
            "バランスの良い食事です",
            "タンパク質の摂取量を増やすことをお勧めします",
            "野菜の摂取量を増やすことで、より良いバランスになります"
        ]
        
        return NutritionAnalysis(
            calories=total_calories,
            protein=total_protein,
            fat=total_fat,
            carbohydrates=total_carbs,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}