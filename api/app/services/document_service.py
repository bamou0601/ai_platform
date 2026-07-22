"""
機能: 文書管理サービス
ロジック: 文書のEmbedding生成およびQdrantへの登録処理を管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

from uuid import uuid4

from app.config import settings
from app.repositories.vector_repository import VectorRepository
from app.schemas.document import DocumentUpsertResponse
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
