"""
機能: Prompt Template Service
ロジック: Prompt Templateのビジネスロジック
"""

from sqlalchemy.orm import Session

from app.repositories.prompt_template_repository import PromptTemplateRepository
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate
)


class PromptTemplateService:

    def __init__(self):
        self.repository = PromptTemplateRepository()

    def create_prompt(
        self,
        db: Session,
        prompt: PromptTemplateCreate
    ):
        return self.repository.create(
            db,
            prompt
        )

    def get_prompts(
        self,
        db: Session
    ):
        return self.repository.find_all(db)

    def get_prompt(
        self,
        db: Session,
        prompt_id: int
    ):
        return self.repository.find_by_id(
            db,
            prompt_id
        )

    def update_prompt(
        self,
        db: Session,
        prompt_id: int,
        prompt: PromptTemplateUpdate
    ):
        return self.repository.update(
            db,
            prompt_id,
            prompt
        )

    def delete_prompt(
        self,
        db: Session,
        prompt_id: int
    ):
        return self.repository.delete(
            db,
            prompt_id
        )