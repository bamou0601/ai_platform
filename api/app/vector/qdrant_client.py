"""
機能: Qdrant Client
ロジック: Qdrantへの接続を管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

from qdrant_client import QdrantClient

from app.config import settings


class QdrantVectorClient:
    """
    Qdrant接続クラス。

    Vector Databaseとの接続を管理する。
    """

    def __init__(self):
        """
        QdrantClientを初期化する。
        Returns: None
        """

        self.client = QdrantClient(
            url=settings.qdrant_url,
        )

    def get_client(self) -> QdrantClient:
        """
        QdrantClientを取得する。

        Returns:
            QdrantClient
        """
        return self.client

    def health(self) -> bool:
        """
        Qdrantへ接続できるか確認する。

        Returns:
            bool: 接続成功時True
        """

        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
