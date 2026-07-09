"""
機能: Conversation Repository
ロジック: ConversationテーブルへのCRUD操作
作成者: 馬 猛
作成日: 2026/07/09
"""
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate
)

class ConversationRepository:

    def create(
        self,
        db: Session,
        conversation: ConversationCreate
    ) -> Conversation:
        
        db_conversation = Conversation(
            **conversation.model_dump()
        )

        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)

        return db_conversation

    def find_all(
        self,
        db: Session
    ) -> list[Conversation]:
        
        return db.query(Conversation).all()

    def find_by_id(
        self,
        db: Session,
        conversation_id: int
    ) -> Conversation | None:
        
        return (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def update(
        self,
        db: Session,
        conversation_id: int,
        conversation: ConversationUpdate
    ) -> Conversation | None:
        
        db_conversation = self.find_by_id(db, conversation_id)

        if not db_conversation:
            return None

        update_data = conversation.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_conversation,
                key,
                value
            )

        db.commit()
        db.refresh(db_conversation)

        return db_conversation

    def delete(
        self,
        db: Session,
        conversation_id: int
    ) -> bool:
        
        db_conversation = self.find_by_id(db, conversation_id)

        if not db_conversation:
            return False

        db.delete(db_conversation)
        db.commit()

        return True