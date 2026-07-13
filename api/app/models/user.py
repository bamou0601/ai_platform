"""
機能: UserテーブルのORMモデル
ロジック: Userごとの操作を管理する
作成者: 馬 猛
作成日: 2026/07/02
修正日: 2026/07/10
"""

from datetime import datetime

from sqlalchemy import (
    Column, 
    Integer, 
    String,
    DateTime
) 

from app.db.base import Base

class User(Base):
    """ユーザーテーブル"""

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100), 
        nullable=False
    )


    email = Column(
        String(255), 
        unique=True, 
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )