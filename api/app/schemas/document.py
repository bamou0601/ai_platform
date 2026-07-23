"""
機能: 文書登録および検索APIスキーマ
ロジック: Qdrantへ登録・検索する文書のリクエストおよびレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/22
修正日: 2026/07/23
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


class DocumentSearchRequest(BaseModel):
    """類似文書検索リクエストを定義する。"""

    query: str = Field(
        ...,
        min_length=1,
        description="類似文書を検索するためのテキスト",
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=20,
        description="取得する検索結果の最大件数",
    )

    score_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="検索結果に含める最低類似度",
    )


class DocumentSearchResult(BaseModel):
    """類似文書検索結果を定義する。"""

    point_id: str
    score: float
    text: str
    source: str | None


class DocumentSearchResponse(BaseModel):
    """類似文書検索レスポンスを定義する。"""

    success: bool
    query: str
    count: int
    results: list[DocumentSearchResult]
