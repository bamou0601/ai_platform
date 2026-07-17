"""
機能: Model APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/10
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModelCreate(BaseModel):
    """
    Model登録時のリクエストスキーマ。

    新しいLLMモデルを登録するための
    リクエストデータを定義する。
    """

    name: str
    provider: str
    version: str
    is_active: bool = True


class ModelUpdate(BaseModel):
    """
    Model更新時のリクエストスキーマ。

    登録済みのLLMモデル情報を更新するための
    リクエストデータを定義する。
    """

    name: str
    provider: str
    version: str
    is_active: bool


class ModelResponse(BaseModel):
    """
    Model取得時のレスポンススキーマ。

    APIから返却するLLMモデル情報を定義する。
    SQLAlchemy ORMオブジェクトからの変換に対応する。
    """

    id: int
    name: str
    provider: str
    version: str
    is_active: bool
    created_at: datetime

    # SQLAlchemy ORMオブジェクトから
    # Pydanticモデルへの変換を有効にする
    model_config = ConfigDict(from_attributes=True)
