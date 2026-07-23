"""
機能: Qdrant関連API
ロジック: Qdrant接続確認、Collection作成およびEmbedding生成APIを提供する
作成者: 馬 猛
作成日: 2026/07/22
"""

from fastapi import APIRouter, HTTPException
from requests import RequestException

from app.config import settings
from app.schemas.document import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentUpsertRequest,
    DocumentUpsertResponse,
)
from app.schemas.embedding import EmbeddingRequest, EmbeddingResponse
from app.schemas.rag import RagChatRequest, RagChatResponse
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RagService
from app.services.vector_service import VectorService
from app.vector.qdrant_client import QdrantVectorClient

router = APIRouter(
    prefix="/qdrant",
    tags=["Qdrant"],
)

qdrant_client = QdrantVectorClient()
vector_service = VectorService()
embedding_service = EmbeddingService()
document_service = DocumentService()
rag_service = RagService()


@router.get("")
def health() -> dict[str, bool]:
    """
    Qdrantへの接続状態を確認する。

    Returns:
        dict[str, bool]: 接続確認結果
    """
    return {
        "success": qdrant_client.health(),
    }


@router.post("/collection")
def create_collection() -> dict[str, bool]:
    """
    Qdrant Collectionを作成する。

    Returns:
        dict[str, bool]: Collection作成結果
    """
    vector_service.create_collection()

    return {"success": True}


@router.post(
    "/embedding",
    response_model=EmbeddingResponse,
)
def create_embedding(
    request: EmbeddingRequest,
) -> EmbeddingResponse:
    """
    入力テキストからEmbeddingを生成する。

    Args:
        request: Embedding生成リクエスト

    Returns:
        EmbeddingResponse: 生成されたEmbedding情報

    Raises:
        HTTPException: Embedding生成に失敗した場合
    """

    try:
        embedding = embedding_service.embed(request.text)

        return EmbeddingResponse(
            model=settings.embedding_model,
            dimension=len(embedding),
            embedding=embedding,
        )

    except RequestException as exception:
        raise HTTPException(
            status_code=503,
            detail="Ollama Embedding APIへ接続できません。",
        ) from exception

    except ValueError as exception:
        raise HTTPException(
            status_code=500,
            detail=str(exception),
        ) from exception


@router.post(
    "/documents",
    response_model=DocumentUpsertResponse,
)
def upsert_document(
    request: DocumentUpsertRequest,
) -> DocumentUpsertResponse:
    """
    文書をEmbedding化してQdrantへ登録する。

    Args:
        request: 文書登録リクエスト

    Returns:
        DocumentUpsertResponse: 文書登録結果

    Raises:
        HTTPException: 文書登録に失敗した場合
    """
    try:
        return document_service.upsert_document(
            text=request.text,
            source=request.source,
        )

    except RequestException as exception:
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to the Ollama Embedding API.",
        ) from exception

    except ValueError as exception:
        raise HTTPException(
            status_code=400,
            detail=str(exception),
        ) from exception

    except RuntimeError as exception:
        raise HTTPException(
            status_code=503,
            detail=str(exception),
        ) from exception


@router.post(
    "/documents/search",
    response_model=DocumentSearchResponse,
)
def search_documents(
    request: DocumentSearchRequest,
) -> DocumentSearchResponse:
    """
    検索文に類似する文書をQdrantから取得する。

    Args:
        request: 類似文書検索リクエスト

    Returns:
        DocumentSearchResponse: 類似文書の検索結果

    Raises:
        HTTPException: 類似文書検索に失敗した場合
    """
    try:
        return document_service.search_documents(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

    except RequestException as exception:
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to the Ollama Embedding API.",
        ) from exception

    except ValueError as exception:
        raise HTTPException(
            status_code=400,
            detail=str(exception),
        ) from exception

    except RuntimeError as exception:
        raise HTTPException(
            status_code=503,
            detail=str(exception),
        ) from exception


@router.post(
    "/rag/chat",
    response_model=RagChatResponse,
)
def rag_chat(request: RagChatRequest) -> RagChatResponse:
    """
    関連文書を参照して質問への回答を生成する。

    Args:
        request: RAGチャットリクエスト

    Returns:
        RagChatResponse: 回答および参照文書

    Raises:
        HTTPException: RAGチャット処理に失敗した場合
    """

    try:
        return rag_service.chat(
            question=request.question,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

        # return RagChatResponse(**request.model_dump())

    except ValueError as exception:
        raise HTTPException(
            status_code=400, detail=str(exception)
        ) from exception

    except RuntimeError as exception:
        raise HTTPException(
            status_code=503,
            detail=str(exception),
        ) from exception
