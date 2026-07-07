# 機能: UserテーブルのORMモデル

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base

class User(Base):
    """ユーザーテーブル"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, # 重複しない
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )