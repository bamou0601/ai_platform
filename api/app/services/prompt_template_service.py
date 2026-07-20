"""
機能: Prompt Template Service
ロジック: Prompt Templateのビジネスロジックを提供する
create,find_all,find_by_id,find_all_active
find_default,set_default,enable,disable,update,delete
作成者: 馬 猛
作成日: 2026/7/8
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.prompt_template import PromptTemplate
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
    ) -> PromptTemplate:
        """
        プロンプトテンプレートを登録する。

        Args:
            db (Session):
                データベースセッション
            prompt (PromptTemplateCreate):
                登録するプロンプト情報

        Returns:
            PromptTemplate:
                登録したプロンプトテンプレート
        """
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
        """
        プロンプトテンプレート一覧を取得する。

        検索条件、ページング、および並び替えに対応する。

        Args:
            db (Session): データベースセッション
            page (int): 取得するページ番号
            size (int): 1ページ当たりの取得件数
            keyword (str | None): 検索キーワード
            active (bool | None): 有効状態
            sort (str): ソート対象項目
            order (str): ソート順（asc / desc）

        Returns:
            PromptTemplatePage: ページング情報を含むプロンプト一覧
        """
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

    def get(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        指定したプロンプトテンプレートを取得する。

        Args:
            db (Session):
                データベースセッション
            prompt_id (int):
                プロンプトID

        Returns:
            PromptTemplate | None:
                該当するプロンプトテンプレート
        """
        return self.repository.find_by_id(db, prompt_id)

    def update_prompt(
        self,
        db: Session,
        prompt_id: int,
        prompt: PromptTemplateUpdate,
    ) -> PromptTemplate:
        """
        プロンプトテンプレートを更新する。

        Args:
            db (Session): データベースセッション
            prompt_id (int): プロンプトID
            prompt (PromptTemplateUpdate): 更新内容

        Returns:
            PromptTemplate | None: 更新後のプロンプトテンプレート
        """
        return self.repository.update(db, prompt_id, prompt)

    def delete_prompt(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate:
        """
        プロンプトテンプレートを削除する。

        Args:
            db (Session): データベースセッション
            prompt_id (int): プロンプトID

        Returns: 削除成功時はTrue
        """
        return self.repository.delete(db, prompt_id)

    # defaultを取得
    def get_default(self, db: Session) -> PromptTemplate | None:
        """
        デフォルトのプロンプトテンプレートを取得する。

        Args:
            db (Session): データベースセッション

        Returns:
            PromptTemplate: デフォルトのプロンプトテンプレート

        Raises:
            HTTPException:デフォルトプロンプトが存在しない場合
        """
        prompt = self.repository.find_default(db)
        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Default Prompt not found",
            )

        return prompt

    # 有効prompt一覧
    def get_active(self, db: Session) -> list[PromptTemplate]:
        """
        有効なプロンプトテンプレート一覧を取得する。

        Args:
            db (Session): データベースセッション

        Returns:
            list[PromptTemplate]: 有効なプロンプトテンプレート一覧
        """

        return self.repository.find_all_active(db)

    # 有効化
    def enable(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        プロンプトテンプレートを有効化する。

        Args:
            db (Session): データベースセッション
            prompt_id (int): プロンプトID

        Returns:
            PromptTemplate: 有効化したプロンプトテンプレート

        Raises:
            HTTPException: プロンプトが存在しない場合
        """
        prompt = self.repository.enable(db, prompt_id)

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )
        return prompt

    # 無効化
    def disable(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        プロンプトテンプレートを無効化する。

        Args:
            db (Session): データベースセッション
            prompt_id (int): プロンプトID

        Returns:
            PromptTemplate: 無効化したプロンプトテンプレート

        Raises:
            HTTPException: プロンプトが存在しない場合
        """
        prompt = self.repository.disable(db, prompt_id)

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )
        return prompt

    # Default変更
    def set_default(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        デフォルトのプロンプトテンプレートを変更する。

        Args:
            db (Session): データベースセッション
            prompt_id (int): デフォルトに設定するプロンプトID

        Returns:
            PromptTemplate: デフォルトに設定したプロンプトテンプレート

        Raises:
            HTTPException: プロンプトが存在しない場合
        """

        prompt = self.repository.set_default(db, prompt_id)

        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail="Prompt Template not found",
            )
        return prompt
