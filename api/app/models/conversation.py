"""
機能: Conversationテーブル
ロジック: ユーザーごとのチャットセッションを管理する
作成者: 馬 猛
作成日: 2026/07/09
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from datetime import datetime
from app.db.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    title = Column(String(255), nullable=False)
    
    description = Column(String(500))

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
