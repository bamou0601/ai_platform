"""
機能: Prompt Template Repository
ロジック: Prompt TemplateテーブルへのCRUD操作
create,find_all,find_by_id,find_all_active
find_default,set_default,enable,disable,update,delete
作成者: 馬 猛
作成日: 2026/07/08
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_

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
        db: Session,
        page: int = 1,
        size: int = 20,
        keyword: str | None = None,
        active: bool | None = None,
        sort: str = "created_at",
        order: str = "desc"
    ) -> Tuple[int,list[PromptTemplate]]:

        # query生成
        query = db.query(PromptTemplate)

        #filter
        if active is not None:
            query = query.filter(
                PromptTemplate.is_active == active
            )
        
        #search
        if keyword:
            query = query.filter(
                or_(
                    PromptTemplate.name.ilike(f"%{keyword}%"),
                    PromptTemplate.description.ilike(f"%{keyword}%")
                )
            )

        # 件数取得
        total = query.count()

        #sort
        sort_column = getattr(
            PromptTemplate,
            sort,
            PromptTemplate.created_at
        )

        if order == "asc":
            query = query.order_by(
                sort_column.asc()
            )
        else:
            query = query.order_by(
                sort_column.desc()
            )
        
        items = (
            query
            .offset((page - 1) * size).limit(size).all()
        )
        
        return total, items

        # return db.query(PromptTemplate).all()


    def find_by_id(
        self,
        db: Session,
        prompt_id: int
    ) -> PromptTemplate | None:

        return (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.id == prompt_id,
                PromptTemplate.is_active == True
            )
            .first()
        )

    def find_all_active(
        self,
        db: Session
    ):
        return(
            db.query(PromptTemplate)
            .filter(PromptTemplate.is_active == True)
            .all()
        )

    def find_default(
        self,
        db: Session
    ):
        return (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.is_default == True,
                PromptTemplate.is_active == True
            )
            .first()
        )

    def set_default(
        self,
        db: Session,
        prompt_id: int
    ):
        
        db.query(PromptTemplate).update({"is_default": False})

        prompt = (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.id == prompt_id
            )
            .first()
        )

        if prompt is None:
            prompt.is_default = True

        db.commit()
        return prompt

    def enable(
        self,
        db: Session,
        prompt_id: int
    ):
        prompt = self.find_by_id_all(db, prompt_id)
        if prompt:
            prompt.is_active = True
            db.commit()
        
        return prompt


    def disable(
        self,
        db: Session,
        prompt_id: int
    ):
        
        prompt = self.find_by_id_all(db, prompt_id)

        if prompt:
            prompt.is_active = False
            db.commit()
        
        return prompt


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