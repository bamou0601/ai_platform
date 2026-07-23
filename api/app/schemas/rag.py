"""
機能: RAGチャットAPIスキーマ
ロジック: RAGチャットのリクエストおよびレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/23
"""

from pydantic import BaseModel, Field

from app.schemas.document import DocumentSearchResult


class RagChatRequest(BaseModel):
    """RAGチャットリクエストを定義する。"""

    question: str = Field(
        ...,
        min_length=1,
        description="文書を参照して回答する質問",
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=20,
        description="取得する関連文書の最大件数",
    )

    score_threshold: float | None = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="関連文書として使用する最低類似度",
    )


class RagChatResponse(BaseModel):
    """
    RAGチャットレスポンスを定義する。
    回答に使った文書を references として返す
    """

    success: bool
    question: str
    answer: str
    references: list[DocumentSearchResult]
