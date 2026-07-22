"""
機能: Embedding APIスキーマ
ロジック: Embedding生成時のリクエストおよびレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/22
"""

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Embedding生成リクエストを定義する。"""

    text: str = Field(
        ...,
        min_length=1,
        description="Embeddingへ変換するテキスト",
    )


class EmbeddingResponse(BaseModel):
    """Embedding生成レスポンスを定義する。"""

    model: str
    dimension: int
    embedding: list[float]
