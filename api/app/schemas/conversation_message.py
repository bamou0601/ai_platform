"""
機能: Conversation Message APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/09
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationMessageCreate(BaseModel):
    """
    Conversation Messageの登録リクエストを定義する。

    会話に紐づくメッセージを新規登録する際の
    入力データの形式およびバリデーションを定義する。

    Attributes:
        conversation_id (int): 会話ID
        role (str): メッセージ送信者(user / assistant / system)
        content (str): メッセージ内容
        model (str): 使用したLLMモデル名
        prompt_tokens (int): 入力トークン数
        completion_tokens (int): 出力トークン数
    """

    conversation_id: int
    role: str
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int


class ConversationMessageUpdate(BaseModel):
    """
    Conversation Messageの更新リクエストを定義する。

    既存メッセージの内容を更新する際の
    入力データの形式およびバリデーションを定義する。

    Attributes:
        content (str): 更新後のメッセージ内容
    """

    content: str


class ConversationMessageResponse(BaseModel):
    """
    Conversation Messageのレスポンスを定義する。

    メッセージ取得APIで返却するレスポンス形式を定義する。

    Attributes:
        id (int): メッセージID
        conversation_id (int): 会話ID
        role (str): メッセージ送信者
        content (str): メッセージ内容
        prompt_tokens (int): 入力トークン数
        completion_tokens (int): 出力トークン数
        created_at (datetime): 作成日時
    """

    id: int
    conversation_id: int
    role: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
