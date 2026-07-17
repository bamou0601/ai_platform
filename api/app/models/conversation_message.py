"""
機能: Conversation Messageテーブル
ロジック: Conversationごとのメッセージ履歴を管理する
作成者: 馬 猛
作成日: 2026/07/09
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


class ConversationMessage(Base):
    """
    Conversationごとのメッセージ履歴を管理するORMモデル。

    会話内のユーザーおよびAIのメッセージ、利用したモデル、
    トークン数、作成日時をデータベースへ保存する。

    Attributes:
        id (int): メッセージID(主キー)
        conversation_id (int): Conversation ID(conversationsテーブルの外部キー）
        role (str): メッセージの送信者(user / assistant / system)
        content (str): メッセージ内容
        model (str): 利用したAIモデル名
        prompt_tokens (int): 入力トークン数
        completion_tokens (int): 出力トークン数
        created_at (datetime): メッセージ作成日時
    """

    # テーブル名
    __tablename__ = "conversation_messages"

    # メッセージID（主キー）
    id = Column(Integer, primary_key=True, index=True)

    # Conversation ID（conversationsテーブルへの外部キー）
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False,
    )

    # メッセージ送信者（user / assistant / system）
    role = Column(String(20), nullable=False)

    # メッセージ内容
    content = Column(Text, nullable=False)

    # 利用したAIモデル名
    model = Column(String(100), nullable=False)

    # 入力トークン数
    prompt_tokens = Column(Integer, default=0)

    # 出力トークン数
    completion_tokens = Column(Integer, default=0)

    # メッセージ作成日時
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
