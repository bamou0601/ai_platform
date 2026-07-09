"""
機能: Conversation Messageテーブル
ロジック: Conversationごとのメッセージ履歴を管理する
作成者: 馬 猛
作成日: 2026/07/09
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    String,
    DateTime
)

from app.db.base import Base

class ConversationMessage(Base):

    __tablename__ = "conversation_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    model = Column(
        String(100),
        nullable=False
    )

    prompt_tokens = Column(
        Integer,
        default=0
    )

    completion_tokens = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )