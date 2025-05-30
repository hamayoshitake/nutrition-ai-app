#!/bin/bash
# サービス層のテスト実行スクリプト

# カレントディレクトリをスクリプトが存在するディレクトリに変更
cd "$(dirname "$0")"

# functions ディレクトリのパスを取得
FUNCTIONS_DIR="$(cd ../..; pwd)"
echo "関数ディレクトリ: $FUNCTIONS_DIR"

# 仮想環境のアクティベート
if [ -d "$FUNCTIONS_DIR/venv" ]; then
  echo "仮想環境をアクティベート中..."
  source "$FUNCTIONS_DIR/venv/bin/activate"
else
  echo "警告: 仮想環境が見つかりません。グローバル環境で実行します。"
fi

# テスト実行に必要なライブラリがインストールされているか確認
if ! python -c "import pytest" &> /dev/null; then
  echo "pytestをインストール中..."
  pip install pytest pytest-mock
fi

# 環境変数の設定（必要に応じて）
export PYTHONPATH="$FUNCTIONS_DIR:$PYTHONPATH"

# 特定のテストを指定する場合
if [ $# -eq 1 ]; then
  TEST_FILE=$1
  echo "テスト $TEST_FILE を実行中..."
  python -m pytest $TEST_FILE -v
else
  # すべてのテストを実行
  echo "すべてのテストを実行中..."
  python -m pytest . -v
fi

# 終了ステータスを保存
TEST_STATUS=$?

# 仮想環境の非アクティベート
if [ -d "$FUNCTIONS_DIR/venv" ]; then
  deactivate
fi

# 結果の表示
if [ $TEST_STATUS -eq 0 ]; then
  echo "✅ テスト成功!"
else
  echo "❌ テスト失敗!"
fi

exit $TEST_STATUS 