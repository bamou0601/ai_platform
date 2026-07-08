"""
機能: Prompt Templateテーブル
ロジック: AIプロンプトテンプレートを管理する
作成者: 馬 猛
作成日: 2026/07/08
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime
)

from datetime import datetime
from app.db.base import Base

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    category = Column(String(50))

    description = Column(Text)

    system_prompt = Column(Text, nullable=False)

    temperature = Column(Float, default=0.7)

    top_p = Column(Float, default=0.9)

    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )