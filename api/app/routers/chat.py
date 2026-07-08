# """
# 機能: チャット関連 API エンドポイント
# ロジック: リクエストを受け取り、Ollama サービスへ転送して応答を返す
# 作成者: 馬 猛
# 作成日: 2026/07/2
# """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from app.db.dependencies import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
#from sqlalchemy.orm import Session



# ログの設定を初期化
logger = logging.getLogger(__name__)

# チャット関連のエンドポイントを定義するルーター
router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# Ollama サービスの共有インスタンス
service = ChatService()

# チャット送信用のエンドポイント
@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
    ):
    """受け取ったメッセージをサービスに渡して応答を返す"""
    logger.info("POST /chat")
    return service.chat(db, request)