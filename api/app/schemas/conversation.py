"""
機能: Conversation APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/09
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationBase(BaseModel):
    """
    Conversationの共通リクエストスキーマ。

    Conversation登録およびレスポンスで共通して利用する
    基本情報を定義する。
    """

    title: str
    user_id: int


class ConversationCreate(ConversationBase):
    """
    Conversation登録時のリクエストスキーマ。
    ConversationBaseの項目を利用して、
    新しい会話を登録する。
    """

    pass


class ConversationUpdate(BaseModel):
    """
    Conversation更新時のリクエストスキーマ。
    既存の会話タイトルを更新する。
    """

    title: str


class ConversationResponse(ConversationBase):
    """
    Conversation取得時のレスポンススキーマ。

    APIから返却するConversation情報を定義する。
    SQLAlchemy ORMオブジェクトからの変換に対応する。
    """

    id: int
    title: str
    user_id: int
    created_at: datetime

    # SQLAlchemy ORMオブジェクトからPydanticへ変換を許可する
    model_config = ConfigDict(from_attributes=True)
