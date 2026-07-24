"""
機能: Embedding APIスキーマ
ロジック: Embedding生成時のリクエストおよびレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/22
"""

from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Embedding生成リクエストを定義する。"""

    # Embeddingへ変換する元の文章
    # min_length=1により空文字は入力できない
    text: str = Field(
        ...,
        min_length=1,
        description="Embeddingへ変換するテキスト",
    )


class EmbeddingResponse(BaseModel):
    """Embedding生成レスポンスを定義する。"""

    # Embedding生成に使用したモデル名
    # 例: bge-m3
    model: str

    # 生成されたEmbeddingベクトルの次元数
    # bge-m3の場合は1024次元
    dimension: int

    # 入力文章を数値化したEmbeddingベクトル
    # Qdrantへの登録や類似検索に使用する
    embedding: list[float]
