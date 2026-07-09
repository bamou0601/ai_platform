"""
機能: Conversation Message APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/09
"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

class ConversationMessageCreate(BaseModel):
    """
    メッセージ登録
    """
    conversation_id: int
    role: str
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int

class ConversationMessageUpdate(BaseModel):
    """
    メッセージ更新
    """
    content: str

class ConversationMessageResponse(BaseModel):
    """
    メッセージ取得
    """

    id: int
    conversation_id: int
    role: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )