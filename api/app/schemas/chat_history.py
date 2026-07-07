"""
機能: Chat History APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/07
"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

class ChatHistoryCreate(BaseModel):
    """
    会話履歴登録時のリクエストスキーマ
    ユーザID、質問、AI回答、使用モデルを受け取る
    """

    user_id: int
    question: str
    answer: str
    model: str

class ChatHistoryUpdate(BaseModel):
    """
    会話履歴更新時のリクエストスキーマ

    質問、AI回答、使用モデルを更新する。
    """

    question: str
    answer: str
    model: str

class ChatHistoryResponse(BaseModel):
    """会話履歴取得時のレスポンススキーマ
    APIから返却する
    会話履歴情報を定義する。
    """

    id: int
    user_id: int
    question: str
    answer: str
    model: str
    created_at: datetime

    #SQLAlchemy ORMオブジェクトからPydanticへ変換を許可する
    model_config = ConfigDict(from_attributes=True)
    