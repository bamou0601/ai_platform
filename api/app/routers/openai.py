"""
機能: OpenAI互換API Router
ロジック: OpenAI互換エンドポイントを提供する
作成者: 馬 猛
作成日: 2026/07/21
"""

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

# /v1配下にOpenAI互換APIをまとめるRouterを生成する
# 例:
# /v1/chat/completions
# /v1/models
router = APIRouter(
    prefix="/v1",
    tags=["OpenAI Compatible API"],
)

# Routerでは複雑な処理を直接実装せず、
# 実際のチャット処理やモデル取得処理はServiceへ任せる
chat_service = ChatService()
model_service = ModelService()


@router.post(
    "/chat/completions",
    # このAPIは通常のJSONレスポンスだけでなく、
    # StreamingResponseも返すため、
    # FastAPIによる単一のresponse_model検証は使用しない
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
    # リクエストが通常応答かストリーミング応答かを
    # 後からログで確認できるように記録する
    logger.info(
        "Chat completion request received. stream=%s",
        request.stream,
    )

    # stream=Trueの場合は、
    # Ollamaが生成した回答を最後まで待たず、
    # 生成途中の文字列を順番にクライアントへ返す
    if request.stream:
        return StreamingResponse(
            # ChatServiceから返されるIteratorを使用して、
            # SSEデータを少しずつレスポンスとして送信する
            chat_service.chat_completion_stream(
                request=request,
            ),
            # SSE通信であることをクライアントへ通知する
            media_type="text/event-stream",
            headers={
                # ブラウザやProxyによってストリーミングデータが
                # キャッシュされないようにする
                "Cache-Control": "no-cache",
                # HTTP接続を維持しながら、
                # 複数のSSEデータを継続して送信する
                "Connection": "keep-alive",
                # NginxなどのProxyがレスポンスを一旦ため込んでから
                # まとめて送信することを防ぐ
                # これにより生成された文字列をリアルタイムに返しやすくする
                "X-Accel-Buffering": "no",
            },
        )

    # stream=Falseの場合は、
    # LLMが回答を最後まで生成してから
    # 通常のJSONレスポンスとして返却する
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
    # モデル取得の処理はRouterで直接実装せず、
    # ModelServiceへ処理を委譲する
    return model_service.get_models()
