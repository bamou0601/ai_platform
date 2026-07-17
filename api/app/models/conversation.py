"""
機能: Conversationテーブル
ロジック: ユーザーごとのチャットセッションを管理する
作成者: 馬 猛
作成日: 2026/07/09
"""

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from app.db.base import Base


class Conversation(Base):
    """
    ユーザーごとのチャットセッションを管理するORMモデル。

    会話タイトル、説明、利用状態、および作成・更新日時を
    データベースへ保存する。

    Attributes:
        id (int): Conversation ID (主キー)
        user_id (int): ユーザーID
        title (str): 会話タイトル
        description (str): 会話の説明
        is_active (bool): 会話の有効状態
        created_at (datetime): 作成日時
        updated_at (datetime): 更新日時
    """

    # テーブル名
    __tablename__ = "conversations"

    # Conversation ID（主キー）
    id = Column(Integer, primary_key=True, index=True)

    # ユーザーID
    user_id = Column(Integer, nullable=False)

    # 会話タイトル
    title = Column(String(255), nullable=False)

    # 会話の説明
    description = Column(String(500))

    # 会話の有効状態
    is_active = Column(Boolean, default=True)

    # 作成日時
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # 更新日時
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
