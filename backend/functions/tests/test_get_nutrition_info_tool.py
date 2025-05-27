#!/usr/bin/env python3
"""
新しい統合ツールを使用するエージェントの検証スクリプト
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# backend/functions 直下をモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from agents import Agent, Runner
from function_tools.get_nutrition_info_tool import get_nutrition_info_tool
from function_tools.nutrition_tools import save_nutrition_entry_tool

# テスト用エージェント（統合ツール使用）
test_agent = Agent(
    name="TestAgent",
    model="gpt-4o-mini",
    instructions="""
    栄養情報テスト用エージェントです。
    
    動作ルール：
    1. 栄養情報を聞かれた場合は、get_nutrition_info_toolで一括取得してください
    2. このツールは検索→詳細取得→整理まで自動実行します
    3. 取得した情報を分かりやすく整理して回答してください
    4. エラーが発生した場合は、エラー内容を報告してください
    """,
    tools=[get_nutrition_info_tool, save_nutrition_entry_tool]
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
            
            print(f"✅ 実行成功")
            print(f"🤖 エージェント応答: {result.final_output[:300]}...")
            
            # ツール呼び出し確認
            if hasattr(result, 'tool_calls') and result.tool_calls:
                called_tools = [call.tool_name for call in result.tool_calls]
                print(f"🔧 呼び出されたツール: {called_tools}")
                
                if test_case['expected_tool'] in called_tools:
                    print(f"✅ 期待されたツールが呼び出されました")
                else:
                    print(f"⚠️ 期待されたツール({test_case['expected_tool']})が呼び出されませんでした")
            else:
                print(f"ℹ️ ツール呼び出し情報が取得できませんでした")
            
        except Exception as e:
            print(f"❌ エラー発生: {str(e)}")
            print(f"❌ エラータイプ: {type(e).__name__}")
    
    print(f"\n🏁 === 検証完了 ===")
    print(f"⏰ 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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

if __name__ == "__main__":
    print("🚀 新しい統合ツール検証スクリプト開始")
    
    # 1. ツール直接テスト
    test_tool_directly()
    
    # 2. エージェント経由テスト
    print("\n" + "="*60)
    asyncio.run(test_nutrition_agent())
    
    print("\n✅ 全テスト完了") 