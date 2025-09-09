# 日本時間設定とConfigファイル使用ガイド

## 概要

このプロジェクトでは、日本時間（JST, UTC+9）での日時操作を統一的に行うための設定ファイルとユーティリティモジュールを提供しています。

## ファイル構成

```
backend/functions/
├── config.py                          # アプリケーション設定ファイル
├── api/utils/datetime_utils.py         # 日時ユーティリティモジュール
├── api/utils/test_datetime_utils.py    # テストファイル
└── README_datetime_config.md           # このドキュメント
```

## 1. config.py - 設定ファイル

### 主な機能

- 日本時間（JST）の定義
- 環境変数の管理
- アプリケーション全体の設定

### 使用例

```python
from config import config, JST

# タイムゾーン取得
timezone = config.get_timezone()  # JST (UTC+9)

# 環境判定
if config.is_development():
    print("開発環境です")

# 設定値取得
api_timeout = config.API_TIMEOUT
openai_model = config.OPENAI_MODEL
```

### 主な設定項目

| 設定項目 | 説明 | デフォルト値 |
|---------|------|-------------|
| `JST` | 日本時間タイムゾーン | UTC+9 |
| `ENVIRONMENT` | 実行環境 | development |
| `DEBUG` | デバッグモード | True |
| `API_TIMEOUT` | APIタイムアウト（秒） | 120 |
| `OPENAI_MODEL` | OpenAIモデル | gpt-4o |

## 2. datetime_utils.py - 日時ユーティリティ

### 主な機能

- 日本時間での現在日時取得
- 日時フォーマット変換
- タイムゾーン変換
- システムメッセージ用日時情報生成

### 基本的な使用例

```python
from api.utils.datetime_utils import (
    now_jst, jst_date, jst_datetime, jst_time,
    get_system_datetime_info
)

# 現在の日本時間取得
current_jst = now_jst()  # datetime object with JST

# 文字列形式で取得
today = jst_date()       # "2025-05-26"
now_str = jst_datetime() # "2025-05-26 08:15:46"
time_str = jst_time()    # "08:15:46"

# システムメッセージ用の詳細情報
system_info = get_system_datetime_info()
# {
#   "current_datetime": "2025-05-26 08:15:46",
#   "current_date": "2025-05-26",
#   "current_time": "08:15:46",
#   "timezone": "Asia/Tokyo (JST, UTC+9)",
#   "weekday": "Monday",
#   "weekday_jp": "月",
#   "week_start": "2025-05-26",
#   "month_start": "2025-05-01"
# }
```

### 高度な使用例

```python
from datetime import datetime, timezone
from api.utils.datetime_utils import (
    to_jst, format_jst_date, is_today_jst,
    get_week_start_jst, get_month_start_jst
)

# UTC時刻をJSTに変換
utc_time = datetime.now(timezone.utc)
jst_time = to_jst(utc_time)

# カスタムフォーマット
formatted = format_jst_date(jst_time, "%Y年%m月%d日")  # "2025年05月26日"

# 日付判定
is_today = is_today_jst("2025-05-26")  # True/False

# 期間の開始日取得
week_start = get_week_start_jst()   # "2025-05-26" (今週の月曜日)
month_start = get_month_start_jst() # "2025-05-01" (今月の1日)
```

## 3. エージェントでの使用方法

### システムメッセージに日時情報を含める

```python
from api.utils.datetime_utils import get_system_datetime_info

def create_system_message():
    datetime_info = get_system_datetime_info()
    
    system_message = f"""
あなたは栄養管理AIアシスタントです。

現在の日時情報:
- 日時: {datetime_info['current_datetime']}
- 日付: {datetime_info['current_date']}
- 時刻: {datetime_info['current_time']}
- タイムゾーン: {datetime_info['timezone']}
- 曜日: {datetime_info['weekday_jp']}曜日

重要な指示:
1. 食事記録を保存する際は、必ず現在の日付（{datetime_info['current_date']}）を使用してください
2. 「今日」「本日」と言われた場合は {datetime_info['current_date']} を指します
3. 日本時間基準で処理を行ってください
"""
    return system_message
```

### 栄養サービスでの使用

```python
from api.utils.datetime_utils import jst_date
from services.nutrition_service import NutritionService

class NutritionService:
    def save_entry(self, user_id: str, food_data: dict, entry_date: str = None):
        # entry_dateが指定されていない場合は現在の日本時間の日付を使用
        if not entry_date:
            entry_date = jst_date()
        
        # Firestoreに保存
        # ...
```

## 4. 環境変数設定

### .env ファイルの例

```bash
# 環境設定
ENVIRONMENT=development
DEBUG=True

# Firebase設定
FIREBASE_PROJECT_ID=nutrition-ai-app
FIRESTORE_EMULATOR_HOST=localhost:8080

# OpenAI設定
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# API設定
API_TIMEOUT=120
MAX_RETRIES=3

# ログ設定
LOG_LEVEL=INFO
```

## 5. テスト実行

```bash
# datetime_utilsのテスト実行
python -m pytest api/utils/test_datetime_utils.py -v

# 動作確認
python -c "from api.utils.datetime_utils import get_system_datetime_info; print(get_system_datetime_info())"
```

## 6. トラブルシューティング

### よくある問題

1. **インポートエラー**

   ```python
   # 正しいインポート方法
   from config import config, JST
   from api.utils.datetime_utils import jst_date
   ```

2. **古い日付が保存される問題**

   ```python
   # 問題のあるコード
   entry_date = "2023-10-06"  # ハードコードされた古い日付
   
   # 修正後
   from api.utils.datetime_utils import jst_date
   entry_date = jst_date()  # 現在の日本時間の日付
   ```

3. **タイムゾーンの混在**

   ```python
   # 問題のあるコード
   from datetime import datetime
   now = datetime.now()  # ローカルタイムゾーン
   
   # 修正後
   from api.utils.datetime_utils import now_jst
   now = now_jst()  # 明確に日本時間
   ```

## 7. ベストプラクティス

1. **統一的な日時取得**
   - `datetime.now()`の代わりに`now_jst()`を使用
   - 日付文字列が必要な場合は`jst_date()`を使用

2. **エージェントでの日時情報提供**
   - システムメッセージに`get_system_datetime_info()`の結果を含める
   - 現在日付を明示的に指示

3. **設定の一元管理**
   - 環境依存の設定は`config.py`で管理
   - 環境変数を活用

4. **テストの実行**
   - 新しい機能追加時は必ずテストを実行
   - 日時関連のロジックは特に注意深くテスト

これらの設定とユーティリティを使用することで、日本時間での一貫した日時処理が可能になり、以前発生していた古い日付が保存される問題を解決できます。
