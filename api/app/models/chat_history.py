"""
機能: 会話履歴テーブルのORMモデル
ロジック: AIとの会話履歴を保持する
作成者: 馬 猛
作成日: 2026/07/07
修正日: 2026/07/10
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

class ChatHistory(Base):
    """AIとの会話履歴"""

    __tablename__ = "chat_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    answer = Column(
        Text,
        nullable=False
    )

    model = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )