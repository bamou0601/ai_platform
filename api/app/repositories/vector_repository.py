"""
機能: ベクトルデータ操作
ロジック: QdrantのCollection操作を管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    UpdateStatus,
    VectorParams,
)

from app.config import settings
from app.vector.qdrant_client import QdrantVectorClient

logger = logging.getLogger(__name__)


class VectorRepository:
    """Qdrantのベクトルデータ操作を管理する。"""

    def __init__(self) -> None:
        """QdrantClientを初期化する。"""

        self.client = QdrantVectorClient().get_client()

    def create_collection(self) -> bool:
        """
        Collectionが存在しない場合に作成する。

        Returns:
            bool: 新規作成した場合はTrue、既存の場合はFalse
        """

        collections = self.client.get_collections()

        names = [
            collection.name for collection in collections.collections
        ]

        if settings.qdrant_collection in names:
            return

        self.client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimension,
                distance=Distance.COSINE,
            ),
        )

        return True

    def upsert_document(
        self,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """
        文書ベクトルとPayloadをQdrantへ登録する。

        Args:
            point_id: Qdrantへ登録するPoint ID
            vector: 文書から生成したEmbeddingベクトル
            payload: 文書情報を保持するPayload

        Raises:
            ValueError: 入力値またはUpsert結果が不正な場合
            RuntimeError: Qdrantへの登録に失敗した場合
        """

        if not point_id:
            raise ValueError("Point ID must not be empty.")

        if not vector:
            raise ValueError("Vector must not be empty.")

        if len(vector) != settings.embedding_dimension:
            raise ValueError(
                "Vector dimension does not match the configured "
                "embedding dimension. "
                f"expected={settings.embedding_dimension}, "
                f"actual={len(vector)}"
            )

        if not payload:
            raise ValueError("Payload must not be empty.")

        try:
            logger.info(
                "Upserting document into Qdrant. "
                "collection=%s point_id=%s dimension=%d",
                settings.qdrant_collection,
                point_id,
                len(vector),
            )

            result = self.client.upsert(
                collection_name=settings.qdrant_collection,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                ],
                wait=True,
            )

        except Exception as exception:
            logger.exception(
                "Failed to upsert document into Qdrant. "
                "collection=%s point_id=%s",
                settings.qdrant_collection,
                point_id,
            )

            raise RuntimeError(
                "Failed to upsert the document into Qdrant."
            ) from exception

        if result.status != UpdateStatus.COMPLETED:
            raise RuntimeError(
                "Qdrant upsert operation was not completed. "
                f"status={result.status}"
            )

        logger.info(
            "Document was successfully upserted into Qdrant. "
            "collection=%s point_id=%s",
            settings.qdrant_collection,
            point_id,
        )

    def search_similar(
        self,
        vector: list[float],
        limit: int,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        指定されたベクトルに類似する文書を検索する。

        Args:
            vector: 検索テキストから生成したEmbeddingベクトル
            limit: 取得する検索結果の最大件数
            score_threshold: 検索結果に含める最低類似度

        Returns:
            list[dict[str, Any]]: 類似文書の検索結果

        Raises:
            ValueError: 検索条件が不正な場合
            RuntimeError: Qdrantでの検索に失敗した場合
        """

        if not vector:
            raise ValueError("Search vector must not be empty.")

        if len(vector) != settings.embedding_dimension:
            raise ValueError(
                "Search vector dimension does not match the configured "
                "embedding dimension. "
                f"expected={settings.embedding_dimension}, "
                f"actual={len(vector)}"
            )

        if limit < 1:
            raise ValueError(
                "Search result limit must be greater than zero."
            )

        try:
            logger.info(
                "Searching similar documents in Qdrant. "
                "collection=%s limit=%d score_threshold=%s",
                settings.qdrant_collection,
                limit,
                score_threshold,
            )

            response = self.client.query_points(
                collection_name=settings.qdrant_collection,
                query=vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

        except Exception as exception:
            logger.exception(
                "Failed to search similar documents in Qdrant. "
                "collection=%s",
                settings.qdrant_collection,
            )

            raise RuntimeError(
                "Failed to search similar documents in Qdrant."
            ) from exception

        results: list[dict[str, Any]] = []

        for point in response.points:
            payload = point.payload or {}

            results.append(
                {
                    "point_id": str(point.id),
                    "score": float(point.score),
                    "text": str(payload.get("text", "")),
                    "source": payload.get("source"),
                }
            )
        logger.info(
            "Similar document search completed. "
            "collection=%s result_count=%d",
            settings.qdrant_collection,
            len(results),
        )

        return results
