"""
機能: 文書登録APIスキーマ
ロジック: Qdrantへ登録する文書のリクエストおよびレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/22
"""

from pydantic import BaseModel, Field


class DocumentUpsertRequest(BaseModel):
    """文書登録リクエストを定義する。"""

    text: str = Field(
        ...,
        min_length=1,
        description="Qdrantへ登録するテキスト",
    )

    source: str | None = Field(
        default=None,
        description="文書の取得元",
    )


class DocumentUpsertResponse(BaseModel):
    """文書登録レスポンスを定義する。"""

    success: bool
    point_id: str
    collection_name: str
