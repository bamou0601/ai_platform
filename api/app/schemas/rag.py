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

    # ユーザーから入力された質問
    # この質問をEmbeddingへ変換し、
    # Qdrantから関連する文書を検索する
    question: str = Field(
        ...,
        min_length=1,
        description="文書を参照して回答する質問",
    )

    # Qdrantから取得する関連文書の最大件数
    # デフォルトでは類似度が高い文書を最大3件取得する
    limit: int = Field(
        default=3,
        ge=1,
        le=20,
        description="取得する関連文書の最大件数",
    )

    # RAGのコンテキストとして使用する文書の最低類似度
    # 例: 0.5の場合、類似度0.5以上の文書だけを使用する
    # Noneを指定した場合は類似度による絞り込みを行わない
    score_threshold: float | None = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="関連文書として使用する最低類似度",
    )


class RagChatResponse(BaseModel):
    """
    RAGチャットレスポンスを定義する。
    LLMが生成した回答と、
    回答生成時に参照した文書を返す。
    """

    # RAGチャット処理の成功・失敗
    success: bool
    # ユーザーから受け取った元の質問
    question: str

    # Qdrantから取得した関連文書を参考に、
    # LLMが生成した回答
    answer: str

    # 回答生成時にRAGのコンテキストとして使用した文書一覧
    # 関連文書が見つからなかった場合は空リストになる
    references: list[DocumentSearchResult]
