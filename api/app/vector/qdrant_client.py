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

        # .envからQdrantの接続先URLを取得し、
        # Qdrantを操作するためのClientを生成する
        #
        # 例:
        # QDRANT_URL=http://localhost:6333
        self.client = QdrantClient(
            url=settings.qdrant_url,
        )

    def get_client(self) -> QdrantClient:
        """
        QdrantClientを取得する。

        RepositoryなどからQdrantを操作するときに使用する。

        Returns:
            QdrantClient:
                初期化済みのQdrantClient
        """

        # __init__で生成したQdrantClientを呼び出し元へ返す
        return self.client

    def health(self) -> bool:
        """
        Qdrantへ接続できるか確認する。

        Returns:
            bool: 接続成功時True、失敗時はFalse
        """

        try:
            # Collection一覧を取得してQdrantとの通信を確認する
            #
            # 正常に取得できればQdrantへ接続できていると判断する
            self.client.get_collections()
            # 例外が発生しなかったため接続成功
            return True
        except Exception:
            # Qdrantが停止している場合や、
            # URL・ポートなどの接続設定が間違っている場合は
            # 例外が発生するため接続失敗としてFalseを返す
            return False
