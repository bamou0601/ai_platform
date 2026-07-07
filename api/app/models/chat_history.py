"""
機能: 会話履歴テーブルのORMモデル
ロジック: AIとの会話履歴を保持する
作成者: 馬 猛
作成日: 2026/07/07
"""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base

class ChatHistory(Base):
    """AIとの会話履歴"""

    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True 
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )