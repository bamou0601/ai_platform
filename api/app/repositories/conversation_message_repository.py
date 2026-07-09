"""
機能: Conversation Message Repository
ロジック: Conversation_MessagesテーブルへのCRUD操作
作成者: 馬 猛
作成日: 2026/07/09
"""
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.schemas.conversation_message import (
    ConversationMessageCreate,
    ConversationMessageUpdate
)

class ConversationMessageRepository:

    def create(
        self,
        db: Session,
        conversation_message: ConversationMessageCreate
    ) -> ConversationMessage:
        
        db_conversation_message = ConversationMessage(
            **conversation_message.model_dump()
        )

        db.add(db_conversation_message)
        db.commit()
        db.refresh(db_conversation_message)

        return db_conversation_message

    def find_all(
        self,
        db: Session
    ) -> list[ConversationMessage]:
        
        return db.query(ConversationMessage).all()

    def find_by_id(
        self,
        db: Session,
        conversation_message_id: int
    ) -> ConversationMessage | None:
        
        return (
            db.query(ConversationMessage)
            .filter(ConversationMessage.id == conversation_message_id)
            .first()
        )

    def update(
        self,
        db: Session,
        conversation_message_id: int,
        conversation_message: ConversationMessageUpdate
    ) -> ConversationMessage | None:
        
        db_conversation_message = self.find_by_id(db, conversation_message_id)

        if not db_conversation_message:
            return None

        update_data = conversation_message.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_conversation_message,
                key,
                value
            )

        db.commit()
        db.refresh(db_conversation_message)

        return db_conversation_message

    def delete(
        self,
        db: Session,
        conversation_message_id: int
    ) -> bool:
        
        db_conversation_message = self.find_by_id(db, conversation_message_id)

        if not db_conversation_message:
            return False

        db.delete(db_conversation_message)
        db.commit()

        return True