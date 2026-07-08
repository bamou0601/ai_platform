"""
機能: Prompt Template Repository
ロジック: Prompt TemplateテーブルへのCRUD操作
作成者: 馬 猛
作成日: 2026/07/08
"""

from sqlalchemy.orm import Session

from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate
)


class PromptTemplateRepository:

    def create(
        self,
        db: Session,
        prompt: PromptTemplateCreate
    ) -> PromptTemplate:

        db_prompt = PromptTemplate(**prompt.model_dump())

        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)

        return db_prompt


    def find_all(
        self,
        db: Session
    ) -> list[PromptTemplate]:

        return db.query(PromptTemplate).all()


    def find_by_id(
        self,
        db: Session,
        prompt_id: int
    ) -> PromptTemplate | None:

        return (
            db.query(PromptTemplate)
            .filter(PromptTemplate.id == prompt_id)
            .first()
        )


    def update(
        self,
        db: Session,
        prompt_id: int,
        prompt: PromptTemplateUpdate
    ) -> PromptTemplate | None:

        db_prompt = self.find_by_id(
            db,
            prompt_id
        )

        if not db_prompt:
            return None

        update_data = prompt.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_prompt,
                key,
                value
            )

        db.commit()
        db.refresh(db_prompt)

        return db_prompt


    def delete(
        self,
        db: Session,
        prompt_id: int
    ) -> bool:

        db_prompt = self.find_by_id(
            db,
            prompt_id
        )

        if not db_prompt:
            return False

        db.delete(db_prompt)
        db.commit()

        return True