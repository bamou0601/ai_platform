"""
機能: 文書登録および検索APIスキーマ
ロジック: Qdrantへ登録・検索する文書のリクエストおよびレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/22
修正日: 2026/07/23
"""

from pydantic import BaseModel, Field


class DocumentUpsertRequest(BaseModel):
    """Qdrantへ文書を登録するリクエストを定義する。"""

    # Qdrantへ登録し、Embedding生成の対象となる文章
    # min_length=1により空文字は入力できない
    text: str = Field(
        ...,
        min_length=1,
        description="Qdrantへ登録するテキスト",
    )

    # 文書の取得元を保持する
    # 任意項目のため、指定されない場合はNoneになる
    # 例: ファイル名、URL、マニュアル名など
    source: str | None = Field(
        default=None,
        description="文書の取得元",
    )


class DocumentUpsertResponse(BaseModel):
    """Qdrantへの文書登録レスポンスを定義する。"""

    # 文書登録処理の成功・失敗
    success: bool
    # Qdrant上で登録したデータを識別するPoint ID
    point_id: str
    # 文書を登録したQdrantのCollection名
    collection_name: str


class DocumentSearchRequest(BaseModel):
    """Qdrantの類似文書検索リクエストを定義する。"""

    # 類似文書を検索するための検索文
    # この文章をEmbeddingへ変換してQdrantで類似検索を行う
    query: str = Field(
        ...,
        min_length=1,
        description="類似文書を検索するためのテキスト",
    )

    # 検索結果として取得する最大件数
    # デフォルトは3件とし、1～20件の範囲のみ許可する
    limit: int = Field(
        default=3,
        ge=1,
        le=20,
        description="取得する検索結果の最大件数",
    )

    # 検索結果として採用する最低類似度
    # 例: 0.5の場合、類似度0.5以上の文書だけを取得する
    # Noneの場合は最低類似度による絞り込みを行わない
    score_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="検索結果に含める最低類似度",
    )


class DocumentSearchResult(BaseModel):
    """類似文書検索結果を定義する。"""

    # Qdrant上のPoint ID
    point_id: str
    # 検索文と登録文書の類似度
    # 値が高いほど検索文との関連性が高い
    score: float
    # QdrantのPayloadに保存されている元の文章
    text: str
    # 文書の取得元
    # sourceに加えて、file_name、page、chunk_index などのメタデータを持たせる拡張もできる
    # 登録されていない場合はNone
    source: str | None


class DocumentSearchResponse(BaseModel):
    """Qdrantの類似文書検索レスポンスを定義する。"""

    # 類似文書検索処理の成功・失敗
    success: bool
    # 実際に検索で使用した検索文
    query: str
    # 検索条件に一致した文書件数
    count: int
    # 類似文書の検索結果一覧
    # 検索結果が存在しない場合は空リストになる
    results: list[DocumentSearchResult]
