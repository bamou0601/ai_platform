"""
機能: Conversation APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/09
"""

from datetime import datetime
from pydantic import BaseModel
from pydantic import ConfigDict

class ConversationBase(BaseModel):
    """
    会話登録時のリクエストスキーマ
    会話タイトルとユーザーIDを受け取る。
    """
    title: str
    user_id: int


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    """
    会話更新時のリクエストスキーマ

    会話タイトルを更新する。
    """
    title: str


class ConversationResponse(ConversationBase):
    """
    会話取得時のレスポンススキーマ
    APIから返却する会話情報を定義する。
    """
    id: int
    title: str
    user_id: int
    created_at: datetime

    # SQLAlchemy ORMオブジェクトからPydanticへ変換を許可する
    model_config = ConfigDict(from_attributes=True)