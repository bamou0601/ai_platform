"""
機能:Conversation Message Service
ロジック: Conversation Messageのビジネスロジック
"""

from sqlalchemy.orm import Session

from app.repositories.conversation_message_repository import ConversationMessageRepository
from app.schemas.conversation_message import (
    ConversationMessageCreate,
    ConversationMessageUpdate
)


class ConversationMessageService:

    def __init__(self):
        self.repository = ConversationMessageRepository()

    def create(
            self, 
            db: Session, 
            data: ConversationMessageCreate
    ):
        return self.repository.create(db, data)

    def get_all(
        self, 
        db: Session
    ):
        return self.repository.find_all(db)

    def get(
        self, 
        db: Session, 
        conversation_message_id: int
    ):
        return self.repository.find_by_id(db, conversation_message_id)
    
    def get_by_conversation(
        self,
        db: Session,
        conversation_id: int
    ):
        return self.repository.find_by_conversation_id(
            db,
            conversation_id
        )

    def update(
        self,
        db: Session,
        conversation_message_id: int,
        data: ConversationMessageUpdate
    ):
        return self.repository.update(
            db,
            conversation_message_id,
            data
        )

    def delete(
        self,
        db: Session,
        conversation_message_id: int
    ):
        return self.repository.delete(
            db,
            conversation_message_id
        )