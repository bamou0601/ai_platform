# """
# 機能: FastAPI アプリケーションの入口
# ロジック: 設定とルーターを読み込み、ログ初期化後に API を生成する
# 作成者: 馬 猛
# 作成日: 2026/07/2
# """

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logger

# FastAPIを起動時にテーブルを作成する
from app.db.init_db import init_db
from app.exceptions.handlers import (
    register_exception_handlers,
)
from app.middleware.logging import logging_middleware
from app.routers.chat import router as chat_router
from app.routers.chat_history import router as chat_history
from app.routers.conversation import router as conversation
from app.routers.conversation_message import (
    router as conversation_message,
)

# ルーターの読み込み
from app.routers.health import router as health_router
from app.routers.model import router as model
from app.routers.models import router as models_router
from app.routers.prompt_template import (
    router as prompt_template,
)
from app.routers.users import router as users_router

# ログの設定を初期化
setup_logger()

# FastAPI アプリケーションの生成
app = FastAPI(
    title=settings.app_name,
    description="Enterprise Local AI Platform",
    version="1.0.0",
)

# CORS（Cross-Origin Resource Sharing）の設定
# ブラウザから別のサーバー（Origin）へアクセスすることを許可するための設定
# 例：
#   Open WebUI（http://localhost:3000）
#          ↓
#   FastAPI（http://localhost:8000）
# のように異なるポート間で通信する場合に必要
app.add_middleware(
    CORSMiddleware,
    # APIへのアクセスを許可するWebサイト（Origin）の一覧
    # localhost と 127.0.0.1 は同じPCを指すが、
    # ブラウザでは別のOriginとして扱われるため両方許可する
    allow_origins=settings.allow_origins.split(","),
    # CookieやJWTなどの認証情報を送信することを許可する
    # （現在は未使用だが、将来JWT認証を追加するため有効にしている）
    allow_credentials=True,
    # 許可するHTTPメソッド
    # "*" は GET / POST / PUT / DELETE などすべてを許可する
    allow_methods=["*"],
    # 許可するHTTPヘッダー
    # "*" は Authorization や Content-Type などすべてのヘッダーを許可する
    allow_headers=["*"],
)

# ミドルウェアとしてログ記録を追加
app.middleware("http")(logging_middleware)

# 例外ハンドラーを登録
register_exception_handlers(app)


# ルートパス用のヘルスチェックエンドポイント
@app.get("/")
def root():
    """アプリケーションが正常に動作しているか確認するためのエンドポイント"""
    return {"message": "AI Platform is running"}


@app.on_event("startup")
def startup():
    init_db()


# 各ルーターをアプリケーションへ登録
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(models_router)
app.include_router(users_router)
app.include_router(chat_history)
app.include_router(prompt_template)
app.include_router(conversation)
app.include_router(
    conversation_message, tags=["Conversation Messages"]
)
app.include_router(model)
