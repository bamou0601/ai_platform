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
