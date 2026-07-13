"""
機能: Modelテーブル
ロジック: 利用可能なLLMモデルを管理する
作成者: 馬 猛
作成日: 2026/07/10
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from app.db.base import Base

class Model(Base):

    __tablename__ = "models"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    provider = Column(
        String(100),
        nullable=False
    )

    version = Column(
        String(50)
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )