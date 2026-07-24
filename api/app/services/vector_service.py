"""
機能: ベクトルサービス
ロジック: ベクトルDB操作のビジネスロジックを管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

from app.repositories.vector_repository import VectorRepository


class VectorService:
    """ベクトルDBに関する処理を管理する。"""

    def __init__(self) -> None:
        """VectorRepositoryを初期化する。"""

        # Qdrantへの実際のデータ操作を担当するRepositoryを生成する
        #
        # Service層ではQdrantClientを直接操作せず、
        # Repositoryを経由してベクトルDBを操作する
        self.repository = VectorRepository()

    def create_collection(self) -> None:
        """
        QdrantのCollectionを作成する。

        Collectionが存在するかどうかの確認や、
        実際の作成処理はVectorRepositoryへ委譲する。

        Returns:
            None
        """

        # RepositoryへCollection作成処理を依頼する
        #
        # Service層とRepository層を分離することで、
        # API側がQdrantの具体的な操作方法を意識せずに利用できる
        self.repository.create_collection()
