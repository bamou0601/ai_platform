"""
機能: Prompt Template Repository
ロジック: Prompt TemplateテーブルへのCRUD操作
create,find_all,find_by_id,find_all_active
find_default,set_default,enable,disable,update,delete
作成者: 馬 猛
作成日: 2026/07/08
"""

from typing import Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
)


class PromptTemplateRepository:
    def create(
        self, db: Session, prompt: PromptTemplateCreate
    ) -> PromptTemplate:
        """
        プロンプトテンプレートを登録する。

        リクエストスキーマからORMモデルを生成し、
        データベースへ登録した後、登録結果を返却する。

        Args:
            db (Session): SQLAlchemyのデータベースセッション
            prompt (PromptTemplateCreate):
                登録するプロンプトテンプレート情報

        Returns:
            PromptTemplate:
                登録したプロンプトテンプレート
        """

        # ORMモデルを生成
        db_prompt = PromptTemplate(**prompt.model_dump())

        # データベースへ登録
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)

        return db_prompt

    def find_all(
        self,
        db: Session,
        page: int = 1,
        size: int = 20,
        keyword: str | None = None,
        active: bool | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> Tuple[int, list[PromptTemplate]]:
        """
        プロンプトテンプレート一覧を取得する。
        有効・無効状態、キーワード検索、ソート、
        ページング条件を適用し、総件数と一覧を返却する。

        Args:
            db (Session):SQLAlchemyのデータベースセッション
            page (int):取得ページ番号
            size (int):1ページあたりの取得件数
            keyword (str | None):検索キーワード
            active (bool | None):有効・無効状態
            sort (str):ソート対象カラム
            order (str):ソート順（asc / desc）

        Returns:
            tuple[int, list[PromptTemplate]]:
                総件数とプロンプトテンプレート一覧
        """

        # query生成
        query = db.query(PromptTemplate)

        # filter
        if active is not None:
            query = query.filter(PromptTemplate.is_active == active)

        # search
        if keyword:
            query = query.filter(
                or_(
                    PromptTemplate.name.ilike(f"%{keyword}%"),
                    PromptTemplate.description.ilike(f"%{keyword}%"),
                )
            )

        # 件数取得
        total = query.count()

        # sort
        sort_column = getattr(
            PromptTemplate, sort, PromptTemplate.created_at
        )

        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = query.offset((page - 1) * size).limit(size).all()

        return total, items

        # return db.query(PromptTemplate).all()

    def find_by_id(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        IDを指定してプロンプトテンプレートを取得する。

        有効なプロンプトテンプレートのみ検索する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

            prompt_id (int):
                プロンプトテンプレートID

        Returns:
            PromptTemplate | None:
                プロンプトテンプレート。
                存在しない場合はNone
        """

        return (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.id == prompt_id,
                PromptTemplate.is_active == True,
            )
            .first()
        )

    def find_all_active(self, db: Session) -> list[PromptTemplate]:
        """
        有効なプロンプトテンプレート一覧を取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

        Returns:
            list[PromptTemplate]:
                有効なプロンプトテンプレート一覧
        """
        return (
            db.query(PromptTemplate)
            .filter(PromptTemplate.is_active == True)
            .all()
        )

    def find_default(self, db: Session) -> PromptTemplate | None:
        """
        デフォルトのプロンプトテンプレートを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

        Returns:
            PromptTemplate | None:
                デフォルトのプロンプトテンプレート。
                存在しない場合はNone
        """
        return (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.is_default == True,
                PromptTemplate.is_active == True,
            )
            .first()
        )

    def set_default(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        指定したプロンプトテンプレートをデフォルトに設定する。

        既存のデフォルト設定を解除した後、
        指定したテンプレートをデフォルトとして設定する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

            prompt_id (int):
                プロンプトテンプレートID

        Returns:
            PromptTemplate | None:
                更新後のプロンプトテンプレート。
                存在しない場合はNone
        """

        db.query(PromptTemplate).update({"is_default": False})

        prompt = (
            db.query(PromptTemplate)
            .filter(PromptTemplate.id == prompt_id)
            .first()
        )

        if prompt is not None:
            prompt.is_default = True

        db.commit()
        return prompt

    def enable(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        プロンプトテンプレートを有効化する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

            prompt_id (int):
                プロンプトテンプレートID

        Returns:
            PromptTemplate | None:
                更新後のプロンプトテンプレート。
                存在しない場合はNone
        """
        prompt = self.find_by_id(db, prompt_id)
        if prompt:
            prompt.is_active = True
            db.commit()

        return prompt

    def disable(
        self, db: Session, prompt_id: int
    ) -> PromptTemplate | None:
        """
        プロンプトテンプレートを無効化する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

            prompt_id (int):
                プロンプトテンプレートID

        Returns:
            PromptTemplate | None:
                更新後のプロンプトテンプレート。
                存在しない場合はNone
        """

        prompt = self.find_by_id(db, prompt_id)

        if prompt:
            prompt.is_active = False
            db.commit()

        return prompt

    def update(
        self,
        db: Session,
        prompt_id: int,
        prompt: PromptTemplateUpdate,
    ) -> PromptTemplate | None:
        """
        プロンプトテンプレートを更新する。

        指定したプロンプトテンプレートの情報を更新し、
        更新後のデータを返却する。

        Args:
            db (Session): SQLAlchemyのデータベースセッション
            prompt_id (int): プロンプトテンプレートID
            prompt (PromptTemplateUpdate): 更新するプロンプトテンプレート情報

        Returns:
            PromptTemplate | None:
                更新後のプロンプトテンプレート。
                存在しない場合はNone
        """

        db_prompt = self.find_by_id(db, prompt_id)

        if not db_prompt:
            return None

        update_data = prompt.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_prompt, key, value)

        db.commit()
        db.refresh(db_prompt)

        return db_prompt

    def delete(self, db: Session, prompt_id: int) -> bool:
        """
        プロンプトテンプレートを削除する。

        Args:
            db (Session): SQLAlchemyのデータベースセッション

            prompt_id (int): プロンプトテンプレートID

        Returns:
            bool:
                削除に成功した場合はTrue、
                存在しない場合はFalse
        """

        db_prompt = self.find_by_id(db, prompt_id)

        if not db_prompt:
            return False

        db.delete(db_prompt)
        db.commit()

        return True
