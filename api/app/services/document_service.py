"""
機能: 文書管理サービス
ロジック: 文書のEmbedding生成およびQdrantへの登録処理を管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

from uuid import uuid4

from app.config import settings
from app.repositories.vector_repository import VectorRepository
from app.schemas.document import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentSearchResult,
    DocumentUpsertResponse,
)
from app.services.embedding_service import EmbeddingService


class DocumentService:
    """文書のEmbedding生成および登録処理を管理する。"""

    def __init__(self) -> None:
        """必要なServiceおよびRepositoryを初期化する。"""

        self.embedding_service = EmbeddingService()
        self.vector_repository = VectorRepository()

    def upsert_document(
        self,
        text: str,
        source: str | None = None,
    ) -> DocumentUpsertResponse:
        """
        文書をEmbedding化してQdrantへ登録する。

        Args:
            text: Qdrantへ登録するテキスト
            source: 文書の取得元

        Returns:
            DocumentUpsertResponse: 文書登録結果

        Raises:
            ValueError: 文書内容が不正な場合
            RuntimeError: Qdrantへの登録に失敗した場合
        """
        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError("Document text must not be empty.")

        point_id = str(uuid4())

        # 文書からEmbeddingベクトルを生成する
        vector = self.embedding_service.embed(
            normalized_text,
        )

        # 検索結果として返す文書情報をPayloadへ保存する
        payload: dict[str, str] = {
            "text": normalized_text,
        }

        if source:
            payload["source"] = source.strip()

        # QdrantへPointを登録する
        self.vector_repository.upsert_document(
            point_id=point_id,
            vector=vector,
            payload=payload,
        )

        return DocumentUpsertResponse(
            success=True,
            point_id=point_id,
            collection_name=settings.qdrant_collection,
        )

    def search_documents(
        self,
        query: str,
        limit: int = 3,
        score_threshold: float | None = None,
    ) -> DocumentSearchResponse:
        """
        検索文に類似する文書をQdrantから取得する。
        Args:
            query: 類似文書を検索するためのテキスト
            limit: 取得する検索結果の最大件数
            score_threshold: 検索結果に含める最低類似度
        Returns:
            DocumentSearchResponse: 類似文書の検索結果

        Raises:
            ValueError: 検索条件が不正な場合
            RuntimeError: 類似検索に失敗した場合
        """

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Search query must not be empty.")

        # 検索文からEmbeddingベクトルを生成する
        query_vector = self.embedding_service.embed(
            normalized_query,
        )

        # Qdrantから類似文書を取得する
        search_results = self.vector_repository.search_similar(
            vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        results = [
            DocumentSearchResult(
                point_id=result["point_id"],
                score=result["score"],
                text=result["text"],
                source=result["source"],
            )
            for result in search_results
        ]

        return DocumentSearchResponse(
            success=True,
            query=normalized_query,
            count=len(results),
            results=results,
        )
