"""
機能: Chat History APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/07
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatHistoryCreate(BaseModel):
    """
    会話履歴登録時のリクエストスキーマ。

    AIとの会話履歴を新規登録するための
    リクエストデータを定義する。
    """

    user_id: int
    question: str
    answer: str
    model: str


class ChatHistoryUpdate(BaseModel):
    """
    会話履歴更新時のリクエストスキーマ。

    登録済みの会話履歴の質問、回答、
    使用モデル情報を更新する。
    """

    question: str
    answer: str
    model: str


class ChatHistoryResponse(BaseModel):
    """
    会話履歴取得時のレスポンススキーマ。

    APIから返却する会話履歴情報を定義する。
    SQLAlchemy ORMオブジェクトからの変換に対応する。
    """

    id: int
    user_id: int
    question: str
    answer: str
    model: str
    created_at: datetime

    # SQLAlchemy ORMオブジェクトからPydanticへ変換を許可する
    model_config = ConfigDict(from_attributes=True)
