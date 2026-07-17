"""
機能: Prompt Template Service
ロジック: Prompt Templateのビジネスロジックを提供する
create,find_all,find_by_id,find_all_active
find_default,set_default,enable,disable,update,delete
作成者: 馬 猛
作成日: 2026/07/08
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.prompt_template_repository import (
    PromptTemplateRepository,
)
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplatePage,
    PromptTemplateUpdate,
)


class PromptTemplateService:
    """
    Prompt Templateのビジネスロジックを提供するService。

    Repositoryを利用してプロンプトテンプレートの
    登録、取得、更新、削除、および
    デフォルト設定・有効/無効切替を行う。
    """

    def __init__(self):
        """
        Prompt Template Repositoryを初期化する。

        Returns:
            None
        """
        self.repository = PromptTemplateRepository()

    def create_prompt(
        self, db: Session, prompt: PromptTemplateCreate
    ):
        return self.repository.create(db, prompt)

    def get_all(
        self,
        db: Session,
        page: int,
        size: int,
        keyword: str | None,
        active: bool | None,
        sort: str,
        order: str,
    ) -> PromptTemplatePage:
        total, items = self.repository.find_all(
            db=db,
            page=page,
            size=size,
            keyword=keyword,
            active=active,
            sort=sort,
            order=order,
        )

        return PromptTemplatePage(
            total=total, page=page, size=size, items=items
        )

        # return self.repository.find_all(db)

    def get(self, db: Session, prompt_id: int):
        return self.repository.find_by_id(db, prompt_id)

    def update_prompt(
        self,
        db: Session,
        prompt_id: int,
        prompt: PromptTemplateUpdate,
    ):
        return self.repository.update(db, prompt_id, prompt)

    def delete_prompt(self, db: Session, prompt_id: int):
        return self.repository.delete(db, prompt_id)

    # defaultを取得
    def get_default(self, db: Session):
        prompt = self.repository.find_default(db)
        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Default Prompt not found",
            )

        return prompt

    # 有効prompt一覧
    def get_active(self, db: Session):
        return self.repository.find_all_active(db)

    # 有効化
    def enable(self, db: Session, prompt_id: int):
        prompt = self.repository.enable(db, prompt_id)

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )
        return prompt

    # 無効化
    def disable(self, db: Session, prompt_id: int):
        prompt = self.repository.disable(db, prompt_id)

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )
        return prompt

    # Default変更
    def set_default(self, db: Session, prompt_id: int):
        prompt = self.repository.set_default(db, prompt_id)

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )
        return prompt
