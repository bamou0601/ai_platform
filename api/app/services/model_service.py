"""
機能: Model Service
ロジック: Modelのビジネスロジック
作成者: 馬 猛
作成日: 2026/07/10
"""

from sqlalchemy.orm import Session

from app.models.model import Model

from app.repositories.model_repository import ModelRepository

from app.schemas.model import (
    ModelCreate,
    ModelUpdate
)


class ModelService:

    def __init__(self):
        self.repository = ModelRepository()

    def create(
        self,
        db: Session,
        data: ModelCreate
    ) -> Model:

        return self.repository.create(
            db,
            data
        )

    def get_all(
        self,
        db: Session
    ) -> list[Model]:

        return self.repository.find_all(db)

    def get(
        self,
        db: Session,
        model_id: int
    ) -> Model | None:

        return self.repository.find_by_id(
            db,
            model_id
        )

    def update(
        self,
        db: Session,
        model_id: int,
        data: ModelUpdate
    ) -> Model | None:

        return self.repository.update(
            db,
            model_id,
            data
        )

    def delete(
        self,
        db: Session,
        model_id: int
    ) -> bool:

        return self.repository.delete(
            db,
            model_id
        )