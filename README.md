# Nutrition AI App

栄養管理を AI エージェントがサポートするチャットベースのアプリケーションです。自然言語での食事入力から栄養計算、データ保存、不足情報の補完まで、対話形式で完結できます。

## 📋 概要

このアプリケーションは、ユーザーが自由なテキスト形式で食事内容を入力すると、AI エージェントが自動的に食材と量を抽出し、栄養計算を行って記録するシステムです。必要な情報が不足している場合は、対話形式で補完を行います。

### 主な特徴

- **自然言語入力**: 「朝：ご飯170g、納豆1個」のような自由なテキストで食事記録
- **AI による自動抽出**: LLM が食材、量、食事タイプを構造化データとして抽出
- **自動栄養計算**: 抽出された情報から栄養素を自動計算
- **インテリジェントな対話**: 不足情報があれば AI が質問して補完
- **チャット履歴管理**: 会話セッションとメッセージの永続化
- **データクエリ**: 「昨日の摂取カロリーは？」などの質問に対する自動回答

## 🏗️ アーキテクチャ

```
nutrition-ai-app/
├── frontend/          # Next.js フロントエンド
├── backend/           # Firebase Functions (Python)
├── documents/         # 仕様書・設計書
└── tests/            # テスト関連
```

## 🛠️ 技術スタック

### フロントエンド

- **フレームワーク**: Next.js 15.2.4
- **言語**: TypeScript
- **UI ライブラリ**: Radix UI, Tailwind CSS
- **状態管理**: React Context API
- **認証**: Firebase Authentication
- **フォーム**: React Hook Form + Zod

### バックエンド

- **ランタイム**: Python 3.12
- **フレームワーク**: Firebase Functions
- **AI エージェント**: OpenAI Agents SDK
- **データベース**: Firebase Firestore
- **認証**: Firebase Admin SDK

### インフラ

- **ホスティング**: Firebase Hosting
- **データベース**: Firebase Firestore
- **サーバーレス**: Firebase Functions
- **認証**: Firebase Authentication

## 🚀 セットアップ

### 前提条件

- Node.js (最新 LTS 版)
- Python 3.12
- Firebase CLI
- pnpm (推奨)

### インストール

1. **リポジトリのクローン**

```bash
git clone <repository-url>
cd nutrition-ai-app
```

2. **フロントエンドの依存関係をインストール**

```bash
cd frontend
pnpm install
```

3. **バックエンドの依存関係をインストール**

```bash
cd ../backend/functions
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Firebase プロジェクトの設定**

```bash
firebase login
firebase use --add  # プロジェクト ID を選択
```

5. **環境変数の設定**

```bash
# frontend/.env.local を作成
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
# その他の Firebase 設定...

# backend/functions/.env を作成
OPENAI_API_KEY=your_openai_api_key
```

## 💻 開発

### ローカル開発サーバーの起動

1. **Firebase エミュレータの起動**

```bash
firebase emulators:start
```

2. **フロントエンドの開発サーバー起動**

```bash
npm run dev
```

アプリケーションは <http://localhost:3000> でアクセスできます。

### 利用可能なコマンド

```bash
# フロントエンド
npm run dev          # 開発サーバー起動
npm run build        # プロダクションビルド
npm run start        # プロダクションサーバー起動
npm run test         # テスト実行
npm run test:watch   # テスト監視モード
npm run test:coverage # カバレッジ付きテスト

# ルートレベル
npm run dev          # フロントエンド開発サーバー起動
npm run build        # フロントエンドビルド
npm run start        # フロントエンドサーバー起動
```

## 🧪 テスト

### フロントエンドテスト

```bash
cd frontend
npm run test        # 全テスト実行
npm run test:watch  # 監視モード
npm run test:coverage # カバレッジレポート
```

### バックエンドテスト

```bash
cd backend/functions
python -m pytest tests/
```

## 📦 デプロイ

### Firebase へのデプロイ

```bash
# 全体のデプロイ
firebase deploy

# 個別デプロイ
firebase deploy --only hosting      # フロントエンドのみ
firebase deploy --only functions    # バックエンドのみ
firebase deploy --only firestore    # Firestore ルールのみ
```

## 📁 プロジェクト構造

```
nutrition-ai-app/
├── frontend/                    # Next.js アプリケーション
│   ├── app/                    # App Router
│   │   ├── globals.css        # グローバルスタイル
│   │   ├── layout.tsx         # ルートレイアウト
│   │   ├── page.tsx          # ホームページ
│   │   └── login/            # ログインページ
│   ├── components/            # React コンポーネント
│   │   ├── ui/               # UI コンポーネント
│   │   └── ProtectedRoute.tsx # 認証保護コンポーネント
│   ├── contexts/             # React Context
│   ├── hooks/               # カスタムフック
│   ├── lib/                 # ユーティリティ
│   └── __tests__/           # フロントエンドテスト
├── backend/                 # Firebase Functions
│   ├── functions/
│   │   ├── api/            # API エンドポイント
│   │   ├── function_tools/ # AI エージェントツール
│   │   ├── repositories/   # データアクセス層
│   │   ├── services/       # ビジネスロジック
│   │   ├── scripts/        # ユーティリティスクリプト
│   │   ├── tests/          # バックエンドテスト
│   │   └── main.py         # メイン関数
│   ├── firestore.rules     # Firestore セキュリティルール
│   └── firestore.indexes.json # Firestore インデックス
├── documents/              # 仕様書・設計書
├── firebase.json          # Firebase 設定
└── package.json          # ルートパッケージ設定
```

## 🔐 セキュリティ

- Firebase Authentication による認証
- Firestore Security Rules によるデータアクセス制御
- 環境変数による機密情報の管理
- TypeScript による型安全性の確保

## 📊 データベース設計

### 主要なコレクション

- `users`: ユーザー情報
- `nutrition_entries`: 栄養記録
- `chat_sessions`: チャットセッション
- `chat_messages`: チャットメッセージ
- `user_physicals`: ユーザーの身体情報

## 🤖 AI エージェント機能

### 利用可能なツール

- `get_nutrition_info_tool`: 栄養情報取得
- `get_nutrition_search_tool`: 栄養検索
- `calculate_nutrition_summary_tool`: 栄養サマリー計算
- `evaluate_nutrition_search_tool`: 栄養検索評価
- `get_nutrition_details_tool`: 栄養詳細取得
- `get_nutrition_search_guidance_tool`: 栄養検索ガイダンス

## 🐛 トラブルシューティング

### よくある問題

1. **Firebase エミュレータが起動しない**
   - ポートが使用中でないか確認
   - Firebase CLI が最新版か確認

2. **フロントエンドで認証エラー**
   - 環境変数が正しく設定されているか確認
   - Firebase プロジェクト設定を確認

3. **バックエンドでインポートエラー**
   - 仮想環境がアクティベートされているか確認
   - requirements.txt の依存関係がインストールされているか確認

## 📄 ライセンス

このプロジェクトは私的利用のため、ライセンスは設定されていません。

## 👥 貢献

このプロジェクトは現在プライベートプロジェクトです。

## 📞 サポート

問題や質問がある場合は、プロジェクトの Issues を確認してください。
