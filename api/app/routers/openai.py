"""
機能: OpenAI互換API Router
ロジック: OpenAI互換エンドポイントを提供する
作成者: 馬 猛
作成日: 2026/07/21
"""

# from fastapi import Depends
# from sqlalchemy.orm import Session
# from app.db.session import get_db
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ModelListResponse,
)
from app.services.chat_service import ChatService
from app.services.model_service import ModelService

logger = logging.getLogger(__name__)

# Routerを生成
router = APIRouter(
    prefix="/v1",
    tags=["OpenAI Compatible API"],
)

# Serviceを生成
chat_service = ChatService()
model_service = ModelService()


@router.post(
    "/chat/completions",
    response_model=None,
)
def chat_completions(
    request: ChatCompletionRequest,
) -> ChatCompletionResponse | StreamingResponse:
    """
    OpenAI互換チャットAPI。
    streamがtrueの場合はSSE形式、
    falseの場合は通常のJSON形式で返却する。

    Args:
        request(ChatCompletionRequest):
        OpenAI互換チャットリクエスト

    Returns:
        ChatCompletionResponse | StreamingResponse:
            OpenAI互換チャットレスポンス
    """

    logger.info(
        "Chat completion request received. stream=%s",
        request.stream,
    )

    # ストリーミングレスポンスを返却する
    if request.stream:
        return StreamingResponse(
            chat_service.chat_completion_stream(
                request=request,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # 通常レスポンスを返却する
    return chat_service.chat_completion(request=request)


@router.get(
    "/models",
    response_model=ModelListResponse,
)
def get_models() -> ModelListResponse:
    """
    利用可能なモデル一覧を取得する。

    Returns:
        ModelListResponse:
            OpenAI互換モデル一覧
    """

    return model_service.get_models()
