"""
機能: Model APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/10
"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ModelCreate(BaseModel):

    name: str
    provider: str
    version: str
    is_active: bool = True


class ModelUpdate(BaseModel):

    name: str
    provider: str
    version: str
    is_active: bool


class ModelResponse(BaseModel):

    id: int
    name: str
    provider: str
    version: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )