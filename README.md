# AI Platform

ローカル環境で動作するシンプルな AI プラットフォーム API です。FastAPI を用いて、健康チェック、チャット応答、利用可能モデル一覧取得のエンドポイントを提供します。

## 概要

このプロジェクトは、以下の機能を提供します。

- ヘルスチェック API
- チャット送信 API
- モデル一覧取得 API
- Ollama サービスとの連携
- リクエストログ記録ミドルウェア
- 例外ハンドリング
- CORS 設定

## ディレクトリ構成

```text
ai_platform/
├── docker-compose.yml
├── README.md
└── api/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── config.py
        ├── core/
        │   └── logging.py
        ├── exceptions/
        │   └── handlers.py
        ├── middleware/
        │   └── logging.py
        ├── routers/
        │   ├── chat.py
        │   ├── health.py
        │   └── models.py
        ├── schemas/
        │   ├── chat.py
        │   └── models.py
        └── services/
            └── ollama_service.py
```

## 前提条件

- Python 3.10 以上
- pip
- Docker / Docker Compose（任意）

## セットアップ

### 1. 依存関係のインストール

```bash
cd api
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
cd api
uvicorn app.main:app --reload
```

起動後、以下の URL でアクセスできます。

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/chat
- http://127.0.0.1:8000/models
- http://127.0.0.1:8000/docs

## 環境変数

`.env` ファイルに以下の値を設定してください。

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=your-default-model-name
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## API エンドポイント

### GET /

アプリケーションの稼働確認用エンドポイントです。

### GET /health

サーバーの状態を確認するためのエンドポイントです。

レスポンス例:

```json
{
  "status": "UP",
  "message": "AI Platform is running"
}
```

### POST /chat

チャットメッセージを送信して応答を取得します。

リクエスト例:

```json
{
  "message": "こんにちは"
}
```

レスポンス例:

```json
{
  "answer": "..."
}
```

### GET /models

Ollama サービスから利用可能なモデル一覧を取得します。

レスポンス例:

```json
{
  "models": ["llama2", "gpt-4", "custom-model"]
}
```

## Docker で起動する場合

```bash
docker compose up --build
```

## 備考

このプロジェクトは学習・開のサンプル実装です。必要に応じて、実際の AI モデル連携や認証機能を追加できます。"