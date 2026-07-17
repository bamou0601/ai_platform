"""
機能: Model Service
ロジック: Modelのビジネスロジック
作成者: 馬 猛
作成日: 2026/07/10
"""

from sqlalchemy.orm import Session

from app.models.model import Model
from app.repositories.model_repository import (
    ModelRepository,
)
from app.schemas.model import ModelCreate, ModelUpdate


class ModelService:
    """
    Modelのビジネスロジックを提供するService。

    Modelの登録、取得、更新、削除などの
    業務処理をRepositoryへ委譲する。
    """

    def __init__(self):
        """
        ModelServiceを初期化する。

        ModelRepositoryのインスタンスを生成する。

        Returns:
            None
        """
        self.repository = ModelRepository()

    def create(self, db: Session, data: ModelCreate) -> Model:
        """
        Modelを登録する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            data (ModelCreate):
                登録するModel情報

        Returns:
            Model:
                登録したModel
        """
        return self.repository.create(db, data)

    def get_all(self, db: Session) -> list[Model]:
        """
        すべてのModelを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

        Returns:
            list[Model]:
                Model一覧
        """
        return self.repository.find_all(db)

    def get(self, db: Session, model_id: int) -> Model | None:
        """
        指定したModelを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            model_id (int):
                Model ID

        Returns:
            Model | None:
                対象のModel。
                存在しない場合はNoneを返す。
        """
        return self.repository.find_by_id(db, model_id)

    def update(
        self, db: Session, model_id: int, data: ModelUpdate
    ) -> Model | None:
        """
        Modelを更新する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            model_id (int):
                更新対象のModel ID
            data (ModelUpdate):
                更新内容

        Returns:
            Model | None:
                更新後のModel。
                対象が存在しない場合はNoneを返す。
        """
        return self.repository.update(db, model_id, data)

    def delete(self, db: Session, model_id: int) -> bool:
        """
        Modelを削除する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            model_id (int):
                削除対象のModel ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """
        return self.repository.delete(db, model_id)
