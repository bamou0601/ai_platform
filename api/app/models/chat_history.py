"""
機能: 会話履歴テーブルのORMモデル
ロジック: AIとの会話履歴を保持する
作成者: 馬 猛
作成日: 2026/07/07
"""

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.db.base import Base


class ChatHistory(Base):
    """
    AIとの会話履歴を管理するORMモデル。

    ユーザーからの質問、AIの回答、利用したモデル名、
    作成日時をデータベースへ保存する。

    Attributes:
        id (int): 会話履歴ID(主キー)
        user_id (int): ユーザーID(usersテーブルの外部キー)
        question (str): ユーザーからの質問内容
        answer (str): AIが生成した回答内容
        model (str): 利用したAIモデル名
        created_at (datetime): 会話履歴の作成日時
    """

    # テーブル名
    __tablename__ = "chat_history"

    # 会話履歴ID（主キー）
    id = Column(Integer, primary_key=True, index=True)

    # ユーザーID（usersテーブルへの外部キー）
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # ユーザーからの質問
    question = Column(Text, nullable=False)

    # AIが生成した回答
    answer = Column(Text, nullable=False)

    # 利用したAIモデル名
    model = Column(String(100), nullable=False)

    # 会話履歴の作成日時
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
