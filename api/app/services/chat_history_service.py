"""
機能: Chat Historyのビジネスロジック
ロジック: Repositoryを利用して会話履歴を操作する
作成者: 馬 猛
作成日: 2026/07/07
"""

from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryUpdate
)

class ChatHistoryService:
    """
    Chat Historyのビジネスロジックを提供するService
    """

    def __init__(self):
        self.repository = ChatHistoryRepository()

    def create_chat(
            self,
            db: Session,
            chat: ChatHistoryCreate
    ) -> ChatHistory:
        """会話履歴を登録する"""

        return self.repository.create(
            db,
            chat
        )
    
    def get_chats(
            self,
            db: Session
    ) -> list[ChatHistory]:
        """
        全会話履歴を取得する
        """

        return self.repository.find_all(db)
    
    def get_chat(
        self,
        db: Session,
        chat_id: int
    ) -> ChatHistory | None:
        """指定した会話履歴を取得する"""

        return self.repository.find_by_id(
            db,
            chat_id
        )
    
    def update_chat(
        self,
        db: Session,
        chat_id: int,
        chat: ChatHistoryUpdate
    ) -> ChatHistory | None:
        """会話履歴を更新する"""

        return self.repository.update(
            db,
            chat_id,
            chat
        )
    
    def delete_chat(
        self,
        db: Session,
        chat_id: int
    ) -> bool:
        """会話履歴を削除する"""

        return self.repository.delete(
            db,
            chat_id
        )