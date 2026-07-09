"""
機能:Conversation Service
ロジック: Conversationのビジネスロジック
"""

from sqlalchemy.orm import Session

from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate
)


class ConversationService:

    def __init__(self):
        self.repository = ConversationRepository()

    def create(
            self, 
            db: Session, 
            data: ConversationCreate
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
        conversation_id: int
    ):
        return self.repository.find_by_id(db, conversation_id)

    def update(
        self,
        db: Session,
        conversation_id: int,
        data: ConversationUpdate
    ):
        return self.repository.update(
            db,
            conversation_id,
            data
        )

    def delete(
        self,
        db: Session,
        conversation_id: int
    ):
        return self.repository.delete(
            db,
            conversation_id
        )