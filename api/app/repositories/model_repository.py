"""
機能: Model Repository
ロジック: ModelテーブルへのCRUD操作
作成者: 馬 猛
作成日: 2026/07/10
"""

from sqlalchemy.orm import Session

from app.models.model import Model
from app.schemas.model import (
    ModelCreate,
    ModelUpdate
)


class ModelRepository:

    def create(
        self,
        db: Session,
        model: ModelCreate
    ) -> Model:

        db_model = Model(
            **model.model_dump()
        )

        db.add(db_model)
        db.commit()
        db.refresh(db_model)

        return db_model

    def find_all(
        self,
        db: Session
    ) -> list[Model]:

        return db.query(Model).all()

    def find_by_id(
        self,
        db: Session,
        model_id: int
    ) -> Model | None:

        return (
            db.query(Model)
            .filter(Model.id == model_id)
            .first()
        )

    def update(
        self,
        db: Session,
        model_id: int,
        model: ModelUpdate
    ) -> Model | None:

        db_model = self.find_by_id(
            db,
            model_id
        )

        if db_model is None:
            return None

        update_data = model.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_model,
                key,
                value
            )

        db.commit()
        db.refresh(db_model)

        return db_model

    def delete(
        self,
        db: Session,
        model_id: int
    ) -> bool:

        db_model = self.find_by_id(
            db,
            model_id
        )

        if db_model is None:
            return False

        db.delete(db_model)
        db.commit()

        return True