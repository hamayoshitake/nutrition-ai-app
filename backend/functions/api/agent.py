import json
import asyncio
import os
from firebase_functions import https_fn, params
from agents import Agent, Runner, trace
from datetime import timedelta, timezone
import re
import uuid
from typing import Any, Dict, List
from .utils.header import get_cors_headers
from .utils.auth_middleware import extract_user_id_from_request
from .utils.tracing_hooks import DetailedNutritionHooks
from .utils.datetime_utils import get_system_datetime_info, now_jst, to_jst
from services.user_service import UserService
from services.chat_session_service import ChatSessionService
from function_tools.chat_tools import save_chat_message_tool, get_chat_messages_tool
from function_tools.nutrition_tools import (
    save_nutrition_entry_tool, 
    get_nutrition_entry_tool,
    get_nutrition_entries_by_date_tool,
    get_all_nutrition_entries_tool
)
from services.chat_message_service import ChatMessageService
from function_tools.get_nutrition_info_tool import get_nutrition_info_tool
from function_tools.get_nutrition_search_guidance_tool import get_nutrition_search_guidance_tool
from function_tools.evaluate_nutrition_search_tool import evaluate_nutrition_search_tool

# フックインスタンス作成
nutrition_hooks = DetailedNutritionHooks()

main_agent = Agent(
    name="MY BODY COACH Agent",
    model="gpt-4o-mini",
    instructions="""
    あなたは「MY BODY COACH」アプリのメインエージェントです。ユーザーの健康管理をサポートする専門的なアシスタントとして動作します。
    
    重要な動作ルール：
    重要な注意事項：
    - 既存の栄養記録に栄養情報が不足している場合は、必ずget_nutrition_search_guidance_toolを使用してから検索を実行してください
    - 推定値の使用は、ガイダンス→検索の両方が失敗した場合の最後の手段です
    - 栄養情報の問い合わせでは、必ずガイダンス→検索→評価の順序で実行してください

    
    1. 食事内容の報告時の処理：
       - ユーザーが食事内容を報告した場合、以下の順序で処理してください
       - まずget_nutrition_search_guidance_toolで検索ガイダンスを取得してください
       - 日本語の食材名の場合は、翻訳提案を含むガイダンスを取得してください
       - ガイダンスに基づいてget_nutrition_info_toolで栄養情報を取得してください
       - 栄養情報取得後、save_nutrition_entry_toolを使用して栄養記録を保存してください
       - APIが利用できない場合は、以下の推定値を使用してください：
         * ご飯100g: カロリー130kcal, タンパク質2.2g, 炭水化物29g, 脂質0.3g
         * 卵1個: カロリー70kcal, タンパク質6g, 炭水化物0.5g, 脂質5g
         * パン1枚: カロリー160kcal, タンパク質6g, 炭水化物28g, 脂質3g
       - 各食材について1回ずつsave_nutrition_entry_toolを呼び出してください（重複呼び出し禁止）
       - 保存後に「栄養記録を保存しました」と報告してください
    
    2. 栄養情報の問い合わせ時の処理：
        - 栄養情報を聞かれた場合は、まずget_nutrition_search_guidance_toolで検索ガイダンスを取得してください
        - 日本語の食材名の場合は、翻訳提案を含むガイダンスを取得してください
        - ガイダンスに基づいて改善されたクエリでget_nutrition_info_toolを実行してください
        - 検索結果が得られた場合は、evaluate_nutrition_search_toolで結果の品質を評価してください
        - 検索が失敗した場合のみ、一般的な栄養価を回答してください
    
    3. 栄養記録の確認時の処理：
       - 「今日の栄養」「栄養摂取量」「栄養摂取状況」などの問い合わせには、get_nutrition_entries_by_date_toolを使用してください
       - 特定のentry_idが分かっている場合のみget_nutrition_entry_toolを使用してください
    
    4. チャット履歴の確認時の処理：
       - 「履歴」「過去の会話」などの問い合わせには、get_chat_messages_toolを使用してください
    
    5. 栄養検索ガイダンスの提供：
       - 「検索方法」「どう検索すれば」「検索のコツ」などの問い合わせには、get_nutrition_search_guidance_toolを使用してください
       - 日本語の食材名が含まれる場合は、user_inputパラメータに含めて翻訳提案を取得してください
       - 食材カテゴリ（meat, fruit, vegetable等）や検索意図（basic_nutrition, high_protein等）が明確な場合は適切に指定してください
       - ガイダンス結果を分かりやすく整理して、具体的な検索例と改善提案を提示してください
    
    6. 検索結果の評価・改善提案：
       - 「検索結果を評価して」「この結果はどう？」などの問い合わせには、evaluate_nutrition_search_toolを使用してください
       - 検索クエリと結果データが提供された場合、適切な評価フォーカス（accuracy, completeness, relevance）を選択してください
       - 評価結果のスコア、グレード、改善提案を分かりやすく説明してください
       - 次のステップや代替検索戦略も提案してください
    
    7. 統合ワークフロー：
       - 検索ガイダンス → 実際の検索 → 結果評価 → 改善提案の流れを適切に実行してください
       - 日本語入力の場合は、翻訳提案 → 英語検索 → 結果評価の流れを推奨してください
       - エラーが発生した場合は、フォールバック戦略を提示してください
    
    8. ツール使用の原則：
       - 同じツールを連続して複数回呼び出さないでください
       - エラーが発生した場合は、1回だけリトライしてください
       - ツールが失敗した場合は、推定値や一般的な情報で回答してください
       - 本日の日付は、current_datetimeで取得してください
    
    処理フロー例：
    - 食事報告 → get_nutrition_search_guidance_tool → get_nutrition_info_tool → save_nutrition_entry_tool → 保存完了を報告
    - 栄養問い合わせ → get_nutrition_search_guidance_tool → get_nutrition_info_tool → evaluate_nutrition_search_tool → 結果を回答
    - 栄養記録確認 → get_nutrition_entries_by_date_toolで今日の記録を取得 → 結果を表示
    - 検索ガイダンス → get_nutrition_search_guidance_toolでガイダンス取得 → 具体的な提案を提示
    - 検索結果評価 → evaluate_nutrition_search_toolで評価実行 → スコアと改善提案を提示
    - 統合ワークフロー → ガイダンス取得 → 検索実行 → 結果評価 → 次のステップ提案
    
    応答スタイル：
    - 親しみやすく、専門的でありながら分かりやすい説明を心がけてください
    - 健康管理のパートナーとして、励ましとサポートの姿勢を示してください
    - 具体的な数値やデータを提示する際は、その意味や重要性も説明してください
    - エラーや問題が発生した場合も、代替案や解決策を積極的に提案してください
    """,
    tools=[
        save_nutrition_entry_tool,
        get_nutrition_entry_tool,
        get_nutrition_entries_by_date_tool,
        get_all_nutrition_entries_tool,
        get_chat_messages_tool,
        get_nutrition_info_tool,
        get_nutrition_search_guidance_tool,
        evaluate_nutrition_search_tool
    ]
)

# HTTP関数
@https_fn.on_request(timeout_sec=120, secrets=[params.SecretParam("OPENAI_API_KEY")])
def agent(request):
    print("🚀 === Agent関数開始 ===")
    print(f"📍 リクエスト受信時刻: {now_jst()}")
    
    # OPENAI_API_KEYの確認
    try:
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            print(f"✅ OPENAI_API_KEY取得成功: {openai_key[:10]}...")
        else:
            print("❌ OPENAI_API_KEYが設定されていません")
    except Exception as e:
        print(f"❌ OPENAI_API_KEY取得エラー: {e}")
    
    headers = get_cors_headers()
    print(f"📋 CORS headers設定完了: {headers}")
    
    # OPTIONS プレフライト対応
    if request.method == "OPTIONS":
        print("✅ OPTIONSリクエスト処理 - 204レスポンス返却")
        return https_fn.Response("", status=204, headers=headers)

    print(f"📥 リクエストメソッド: {request.method}")
    print(f"📥 リクエストヘッダー: {dict(request.headers)}")
    print(f"📥 リクエストURL: {request.url}")
    print(f"📥 リクエストパス: {request.path}")

    # リクエストボディの詳細ログ
    try:
        print("📦 リクエストボディ解析開始...")
        body = request.get_json(silent=True) or {}
        print(f"📦 解析されたボディ: {body}")
        
        prompt = body.get("prompt")
        print(f"📝 抽出されたプロンプト: {prompt}")
        
        if not prompt:
            print("❌ promptフィールドが見つかりません")
            return https_fn.Response(
                json.dumps({"error": "prompt フィールドが必要です"}),
                status=400,
                headers=headers
            )
        print("✅ プロンプト取得成功")
    except Exception as e:
        print(f"❌ リクエストボディ解析エラー: {e}")
        return https_fn.Response(
            json.dumps({"error": f"リクエスト解析エラー: {str(e)}"}),
            status=400,
            headers=headers
        )

    # 認証処理の詳細ログ
    try:
        print("🔐 認証処理開始...")
        user_id = extract_user_id_from_request(request)
        print(f"🔐 認証結果: user_id={user_id}")
        
        if not user_id:
            print("❌ 認証失敗 - user_idが取得できません")
            return https_fn.Response(
                json.dumps({"error": "認証が必要です"}),
                status=401,
                headers=headers
            )
        print("✅ 認証成功")
    except Exception as e:
        print(f"❌ 認証処理エラー: {e}")
        return https_fn.Response(
            json.dumps({"error": f"認証エラー: {str(e)}"}),
            status=401,
            headers=headers
        )

    # セッション処理の詳細ログ
    try:
        print("🍪 セッション処理開始...")
        session_id = request.cookies.get("session_id")
        print(f"🍪 既存セッションID: {session_id}")
        
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"🆕 新しいセッションID生成: {session_id}")
            ChatSessionService().create_session(user_id)
            print("✅ 新しいセッション作成完了")
        else:
            print("✅ 既存セッション使用")
    except Exception as e:
        print(f"❌ セッション処理エラー: {e}")
        # セッションエラーでも処理を続行
        session_id = str(uuid.uuid4())
        print(f"🔄 フォールバック: 新しいセッションID: {session_id}")

    # 日時情報取得の詳細ログ
    try:
        print("🕐 日時情報取得開始...")
        datetime_info = get_system_datetime_info()
        current_jst = now_jst()
        print(f"🕐 日時情報取得成功: {datetime_info}")
        print(f"🕐 現在の日本時間: {current_jst}")
    except Exception as e:
        print(f"❌ 日時情報取得エラー: {e}")
        datetime_info = {"current_datetime": "取得失敗", "error": str(e)}
        current_jst = now_jst()

    print(f"🔍 === 処理パラメータ確認 ===")
    print(f"👤 user_id: {user_id}")
    print(f"🆔 session_id: {session_id}")
    print(f"📝 prompt: {prompt[:100]}...")
    print(f"🕐 current_jst: {current_jst}")
    print(f"🔍 === パラメータ確認終了 ===")

    # プロンプト分析の詳細ログ
    try:
        print("🔍 プロンプト分析開始...")
        prompt_analysis = nutrition_hooks.analyze_prompt_for_tools(prompt)
        print(f"🔍 === プロンプト分析結果 ===")
        print(f"📝 プロンプトタイプ: {prompt_analysis['prompt_type']}")
        print(f"🔑 検出キーワード: {prompt_analysis['keywords']}")
        print(f"🔧 期待されるツール: {prompt_analysis['expected_tools']}")
        print(f"🔍 === 分析結果終了 ===")
    except Exception as e:
        print(f"❌ プロンプト分析エラー: {e}")
        prompt_analysis = {
            'prompt_type': 'unknown',
            'keywords': [],
            'expected_tools': []
        }

    # メッセージ形式作成の詳細ログ
    try:
        print("📤 メッセージ形式作成開始...")
        formatted_messages = [
            {"role": "system", "content": f"""#SYSTEM_DATA
                user_id: {user_id}
                session_id: {session_id}
                current_datetime: {datetime_info['current_datetime']}
                app_name: MY BODY COACH
                #END_SYSTEM_DATA
            """},
            {"role": "user", "content": prompt}
        ]
        print(f"📤 システムメッセージ作成完了")
        print(f"📤 ユーザーメッセージ作成完了")
        print(f"📤 総メッセージ数: {len(formatted_messages)}")
    except Exception as e:
        print(f"❌ メッセージ形式作成エラー: {e}")
        return https_fn.Response(
            json.dumps({"error": f"メッセージ作成エラー: {str(e)}"}),
            status=500,
            headers=headers
        )

    # ユーザーメッセージ保存の詳細ログ
    try:
        print(f"💾 ユーザーメッセージ保存開始...")
        print(f"💾 保存パラメータ: user_id={user_id}, session_id={session_id}, role=user")
        ChatMessageService().save_message(user_id, session_id, "user", prompt)
        print(f"✅ ユーザーメッセージ保存完了")
    except Exception as e:
        print(f"❌ ユーザーメッセージ保存エラー: {e}")
        # 保存エラーでも処理を続行

    # フックリセットの詳細ログ
    try:
        print("🔄 フックリセット開始...")
        nutrition_hooks.reset()
        print("✅ フックリセット完了")
    except Exception as e:
        print(f"❌ フックリセットエラー: {e}")

    try:
        print(f"🚀 === エージェント実行開始 ===")
        print(f"🤖 エージェント名: {main_agent.name}")
        print(f"🧠 モデル: {main_agent.model}")
        print(f"🔧 利用可能ツール数: {len(main_agent.tools)}")
        
        # エージェント実行前の最終確認
        print(f"📋 実行前チェック:")
        print(f"  - メッセージ数: {len(formatted_messages)}")
        print(f"  - フック準備: ✅")
        print(f"  - トレーシング準備: ✅")
        
        # トレーシング付きでエージェントを実行
        print("🔍 トレーシング開始...")
        with trace("MY BODY COACH Agent Workflow", metadata={"user_id": user_id, "session_id": session_id, "prompt": prompt[:100]}):
            print("🏃 Runner.run実行開始...")
            result = asyncio.run(
                Runner.run(
                    main_agent,
                    formatted_messages,
                    hooks=nutrition_hooks
                )
            )
            print("✅ Runner.run実行完了")

        print(f"🎯 エージェント実行完了")
        
        # 結果の詳細ログ
        agent_response = result.final_output
        print(f"🤖 Agent応答長: {len(agent_response)} 文字")
        print(f"🤖 Agent応答プレビュー: {agent_response[:200]}...")

        # 実行サマリーの詳細ログ
        print("📊 実行サマリー取得開始...")
        summary = nutrition_hooks.get_summary()
        print(f"📊 === 実行サマリー ===")
        print(f"📈 総イベント数: {summary['total_events']}")
        print(f"🔨 ツール呼び出し数: {summary['tool_call_count']}")
        print(f"🧠 LLM生成数: {summary['generation_count']}")
        print(f"❌ エラー数: {summary['error_count']}")
        
        # ツール分析の詳細ログ
        actual_tools = [tc['tool_name'] for tc in summary['tool_calls'] if tc['status'] == 'completed']
        expected_tools = prompt_analysis['expected_tools']
        
        print(f"🔍 === ツール呼び出し分析 ===")
        print(f"🎯 期待されるツール: {expected_tools}")
        print(f"✅ 実際に呼び出されたツール: {actual_tools}")
        
        if expected_tools:
            matched_tools = set(actual_tools) & set(expected_tools)
            missing_tools = set(expected_tools) - set(actual_tools)
            unexpected_tools = set(actual_tools) - set(expected_tools)
            
            print(f"✅ 期待通りに呼び出されたツール: {list(matched_tools)}")
            if missing_tools:
                print(f"⚠️ 期待されたが呼び出されなかったツール: {list(missing_tools)}")
            if unexpected_tools:
                print(f"🔄 期待されていなかったが呼び出されたツール: {list(unexpected_tools)}")
                
            appropriateness_score = len(matched_tools) / len(expected_tools) * 100
            print(f"📊 ツール呼び出し適切性スコア: {appropriateness_score:.1f}%")
        
        if summary['tool_calls']:
            print(f"🔧 ツール呼び出し詳細:")
            for i, tool_call in enumerate(summary['tool_calls'], 1):
                print(f"  {i}. {tool_call['tool_name']} ({tool_call['status']}) - {tool_call['timestamp']}")
        
        if summary['errors']:
            print(f"⚠️ エラー詳細:")
            for i, error in enumerate(summary['errors'], 1):
                print(f"  {i}. {error['error_type']}: {error['error_message']}")
        
        print(f"📊 === サマリー終了 ===")

        # Agentメッセージ保存の詳細ログ
        try:
            print(f"💾 Agentメッセージ保存開始...")
            ChatMessageService().save_message(user_id, session_id, "agent", agent_response)
            print(f"✅ Agentメッセージ保存完了")
        except Exception as e:
            print(f"❌ Agentメッセージ保存エラー: {e}")

        # レスポンス作成の詳細ログ
        print("📦 レスポンス作成開始...")
        
        # Cookie設定の詳細ログ
        headers_with_cookie = headers.copy()
        expires_jst = current_jst + timedelta(days=7)
        expires_utc = expires_jst.astimezone(timezone.utc)
        expires = expires_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers_with_cookie["Set-Cookie"] = (
            f"session_id={session_id}; Path=/; Expires={expires}; HttpOnly; SameSite=None; Secure"
        )
        print(f"🍪 Cookie設定: session_id={session_id}, expires={expires}")
        
        response_data = {
            "message": agent_response,
            "debug_info": {
                "tool_calls": summary['tool_call_count'],
                "llm_generations": summary['generation_count'],
                "errors": summary['error_count'],
                "total_events": summary['total_events'],
                "datetime_info": datetime_info,
                "prompt_analysis": {
                    "type": prompt_analysis['prompt_type'],
                    "keywords": prompt_analysis['keywords'],
                    "expected_tools": prompt_analysis['expected_tools']
                },
                "tool_analysis": {
                    "expected_tools": expected_tools,
                    "actual_tools": actual_tools,
                    "matched_tools": list(set(actual_tools) & set(expected_tools)) if expected_tools else [],
                    "missing_tools": list(set(expected_tools) - set(actual_tools)) if expected_tools else [],
                    "unexpected_tools": list(set(actual_tools) - set(expected_tools)) if expected_tools else []
                }
            }
        }
        
        print(f"📦 レスポンスデータ作成完了")
        print(f"📤 200レスポンス返却準備完了")
        
        return https_fn.Response(
            json.dumps(response_data),
            status=200,
            headers=headers_with_cookie
        )
        
    except Exception as e:
        print(f"❌ === エージェント実行エラー ===")
        print(f"❌ エラー内容: {str(e)}")
        print(f"❌ エラータイプ: {type(e).__name__}")
        print(f"❌ エラー発生時刻: {now_jst()}")
        
        # エラー時の詳細情報
        import traceback
        print(f"❌ スタックトレース:")
        print(traceback.format_exc())
        
        # エラー時サマリーを出力
        try:
            summary = nutrition_hooks.get_summary()
            print(f"📊 === エラー時サマリー ===")
            print(f"📈 総イベント数: {summary['total_events']}")
            print(f"🔨 ツール呼び出し数: {summary['tool_call_count']}")
            print(f"❌ エラー数: {summary['error_count']}")
            if summary['errors']:
                print(f"⚠️ 記録されたエラー:")
                for error in summary['errors']:
                    print(f"  - {error['error_type']}: {error['error_message']}")
            print(f"📊 === エラー時サマリー終了 ===")
        except Exception as summary_error:
            print(f"❌ サマリー取得もエラー: {summary_error}")
        
        print(f"📤 500エラーレスポンス返却")
        
        return https_fn.Response(
            json.dumps({
                "message": "処理中にエラーが発生しました。",
                "error": str(e),
                "error_type": type(e).__name__,
                "debug_info": {
                    "error_type": type(e).__name__,
                    "tool_calls": summary['tool_call_count'] if 'summary' in locals() else 0,
                    "errors": summary['error_count'] if 'summary' in locals() else 1
                }
            }),
            status=500,
            headers=headers
        )