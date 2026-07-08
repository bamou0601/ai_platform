"""
機能：chat historyテーブルのCRUD処理
ロジック：SQLAlchemyを利用して会話履歴を操作する
作成者: 馬 猛
作成日: 2026/07/07
"""
from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryUpdate
)

class ChatHistoryRepository:
    """
    ChatHistoryテーブルに対するCRUDを提供するRepository
    """
    def create(
        self,
        db: Session,
        chat: ChatHistoryCreate
    ) -> ChatHistory:
        """会話履歴を登録する"""

        db_chat = ChatHistory(
            user_id=chat.user_id,
            question=chat.question,
            answer=chat.answer,
            model=chat.model
        )

        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)

        return db_chat
    
    def find_all(
        self,
        db: Session
    ) -> list[ChatHistory]:
        """全会話履歴を取得する"""

        return db.query(ChatHistory).all()
    

    def find_by_id(
        self,
        db: Session,
        chat_id: int
    ) -> ChatHistory | None:
        """指定した会話履歴を取得する"""

        return(
            db.query(ChatHistory)
            .filter(ChatHistory.id == chat_id)
            .first()
        )
    
    def update(
        self,
        db: Session,
        chat_id: int,
        chat: ChatHistoryUpdate
    ) -> ChatHistory | None:
        """会話履歴を更新する"""

        db_chat = (
            db.query(ChatHistory)
            .filter(ChatHistory.id == chat_id)
            .first()
        )

        if db_chat is None:
            return None
        
        db_chat.question = chat.question
        db_chat.answer =chat.answer
        db_chat.model = chat.model

        db.commit()
        db.refresh(db_chat)

        return db_chat
    
    def delete(
        self,
        db: Session,
        chat_id: int
    ) -> bool:
        """会話履歴を削除する"""

        db_chat = (
            db.query(ChatHistory)
            .filter(ChatHistory.id == chat_id)
            .first()
        )

        if db_chat is None:
            return False
        
        db.delete(db_chat)
        db.commit()

        return True
    

