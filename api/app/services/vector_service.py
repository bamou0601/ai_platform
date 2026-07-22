"""
機能: ベクトルサービス
ロジック: ベクトルDB操作のビジネスロジックを管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

from app.repositories.vector_repository import VectorRepository


class VectorService:
    """
    ベクトルサービス。
    """

    def __init__(self) -> None:

        self.repository = VectorRepository()

    def create_collection(self) -> None:
        """
        Collectionを作成する。

        Returns:
            None
        """
        self.repository.create_collection()
