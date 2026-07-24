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

# Qdrant関連APIを「/qdrant」配下にまとめる
# 例:
# /qdrant
# /qdrant/collection
# /qdrant/documents
# /qdrant/documents/search
# /qdrant/rag/chat
router = APIRouter(
    prefix="/qdrant",
    tags=["Qdrant"],
)

# Routerでは複雑な処理を直接実装せず、
# 各ServiceやClientへ実際の処理を委譲する
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
    # QdrantClientからCollection一覧を取得できるか確認し、
    # 接続可能であればTrueを返す
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

    # VectorServiceへCollection作成処理を依頼する
    # Repository側で既存Collectionの有無を確認するため、
    # 同じ名前のCollectionが存在しても重複作成されない
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
        # 入力された文章をEmbeddingServiceへ渡し、
        # OllamaのEmbeddingモデルからベクトルを生成する
        embedding = embedding_service.embed(request.text)

        # 生成されたEmbeddingをAPIレスポンス形式へ変換して返す
        # dimensionには実際に生成されたベクトルの要素数を設定する
        return EmbeddingResponse(
            model=settings.embedding_model,
            dimension=len(embedding),
            embedding=embedding,
        )

    except RequestException as exception:
        # Ollamaへの接続失敗やタイムアウトなど、
        # 外部Embedding APIとの通信に失敗した場合は503を返す
        raise HTTPException(
            status_code=503,
            detail="Ollama Embedding APIへ接続できません。",
        ) from exception

    except ValueError as exception:
        # Embeddingレスポンスの形式や次元数など、
        # データ内容に問題がある場合は500として返す
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
        # DocumentServiceへ文章とsourceを渡す
        #
        # Service内部では以下の処理を行う
        # 1. 文章をEmbeddingへ変換
        # 2. UUID形式のPoint IDを生成
        # 3. Qdrantへvectorとpayloadを登録
        return document_service.upsert_document(
            text=request.text,
            source=request.source,
        )

    except RequestException as exception:
        # Embedding生成時にOllamaへ接続できなかった場合は
        # Service Unavailableとして503を返す
        raise HTTPException(
            status_code=503,
            detail="Ollama Embedding APIへ接続できません。",
        ) from exception

    except ValueError as exception:
        # 空文字、ベクトル次元不一致など、
        # 入力値に問題がある場合は400を返す
        raise HTTPException(
            status_code=400,
            detail=str(exception),
        ) from exception

    except RuntimeError as exception:
        # Qdrantへの登録失敗など、
        # 外部サービス側の処理に失敗した場合は503を返す
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
        # DocumentServiceへ検索条件を渡す
        #
        # Service内部では以下の処理を行う
        # 1. queryをEmbeddingへ変換
        # 2. Qdrantで類似検索
        # 3. score順に検索結果を取得
        return document_service.search_documents(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

    except RequestException as exception:
        # 検索用Embedding生成時に
        # Ollamaへ接続できない場合は503を返す
        raise HTTPException(
            status_code=503,
            detail="Ollama Embedding APIへ接続できません。",
        ) from exception

    except ValueError as exception:
        # queryが空、limitが不正など、
        # 検索条件に問題がある場合は400を返す
        raise HTTPException(
            status_code=400,
            detail=str(exception),
        ) from exception

    except RuntimeError as exception:
        # Qdrantへの接続失敗や検索処理失敗の場合は
        # Service Unavailableとして503を返す
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
        # RagServiceへ質問と検索条件を渡す
        #
        # RagService内部では以下の処理を行う
        # 1. 質問をEmbeddingへ変換
        # 2. Qdrantから関連文書を検索
        # 3. 検索結果をコンテキストとして整形
        # 4. コンテキストと質問をOllamaへ送信
        # 5. 回答と参照文書を返却
        return rag_service.chat(
            question=request.question,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

    except ValueError as exception:
        # 質問が空など、
        # リクエスト内容に問題がある場合は400を返す
        raise HTTPException(
            status_code=400, detail=str(exception)
        ) from exception

    except RuntimeError as exception:
        # 質問が空など、
        # リクエスト内容に問題がある場合は400を返す
        raise HTTPException(
            status_code=503,
            detail=str(exception),
        ) from exception
