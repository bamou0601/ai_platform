"""
機能: 文書管理サービス
ロジック: 文書のEmbedding生成およびQdrantへの登録処理を管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

from uuid import uuid4

from app.config import settings
from app.repositories.vector_repository import VectorRepository
from app.schemas.document import (
    DocumentSearchResponse,
    DocumentSearchResult,
    DocumentUpsertResponse,
)
from app.services.embedding_service import EmbeddingService


class DocumentService:
    """文書のEmbedding生成、登録および類似検索処理を管理する。"""

    def __init__(self) -> None:
        """必要なServiceおよびRepositoryを初期化する。"""

        # 文章をベクトルへ変換するEmbeddingServiceを生成する
        self.embedding_service = EmbeddingService()

        # Qdrantへの登録・検索処理を担当するRepositoryを生成する
        self.vector_repository = VectorRepository()

    def upsert_document(
        self,
        text: str,
        source: str | None = None,
    ) -> DocumentUpsertResponse:
        """
        文書をEmbedding化してQdrantへ登録する。

        Args:
            text: Qdrantへ登録するテキスト
            source: 文書の取得元

        Returns:
            DocumentUpsertResponse: 文書登録結果

        Raises:
            ValueError: 文書内容が不正な場合
            RuntimeError: Qdrantへの登録に失敗した場合
        """

        # 入力文字列の前後にある不要な空白や改行を削除する
        # 例:
        # "  AIプラットフォーム  "
        # ↓
        # "AIプラットフォーム"
        normalized_text = text.strip()

        # 空白を削除した結果、文章が空になった場合は
        # Embedding生成やQdrant登録を行えないためエラーにする
        if not normalized_text:
            raise ValueError("Document text must not be empty.")

        # Qdrant上で文書を一意に識別するPoint IDを生成する
        #
        # uuid4()を使用することで、
        # 文書を登録するたびに重複しにくいIDを自動生成できる
        point_id = str(uuid4())

        # 文書をEmbeddingServiceへ渡し、
        # Qdrantの類似検索で使用する数値ベクトルへ変換する
        #
        # 現在はbge-m3を使用しているため、
        # 1024次元のベクトルが生成される
        vector = self.embedding_service.embed(
            normalized_text,
        )

        # Qdrantではベクトルだけでなく、
        # 元の文章などの付加情報をPayloadとして保存できる
        #
        # 検索後に元文章を取得できるよう、
        # textをPayloadへ保存する
        payload: dict[str, str] = {
            "text": normalized_text,
        }

        # sourceが指定されている場合だけPayloadへ追加する
        #
        # sourceは任意項目なので、
        # Noneや空文字の場合は登録しない
        #
        # 例:
        # source="manual.pdf"
        if source:
            payload["source"] = source.strip()

        # 生成したPoint ID、Embeddingベクトル、Payloadを
        # VectorRepositoryへ渡してQdrantへ登録する
        self.vector_repository.upsert_document(
            point_id=point_id,
            vector=vector,
            payload=payload,
        )

        # 登録成功後、APIへ返すレスポンス形式を作成する
        return DocumentUpsertResponse(
            success=True,
            point_id=point_id,
            collection_name=settings.qdrant_collection,
        )

    def search_documents(
        self,
        query: str,
        limit: int = 3,
        score_threshold: float | None = None,
    ) -> DocumentSearchResponse:
        """
        検索文に類似する文書をQdrantから取得する。
        Args:
            query: 類似文書を検索するためのテキスト
            limit: 取得する検索結果の最大件数
            score_threshold: 検索結果に含める最低類似度
        Returns:
            DocumentSearchResponse: 類似文書の検索結果

        Raises:
            ValueError: 検索条件が不正な場合
            RuntimeError: 類似検索に失敗した場合
        """

        # 検索文の前後にある不要な空白や改行を削除する
        normalized_query = query.strip()

        # 検索文が空の場合はEmbeddingを生成できないため、
        # Qdrant検索を実行せずエラーにする
        if not normalized_query:
            raise ValueError("Search query must not be empty.")

        # 検索文をEmbeddingへ変換する
        #
        # 登録文書と検索文を同じEmbeddingモデルで
        # ベクトル化することで類似度を比較できる
        query_vector = self.embedding_service.embed(
            normalized_query,
        )

        # 検索文のベクトルをQdrantへ渡して、
        # 類似度の高い文書を検索する
        #
        # limit:
        #   最大何件取得するか
        #
        # score_threshold:
        #   最低どの程度の類似度を要求するか
        search_results = self.vector_repository.search_similar(
            vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Repositoryから返されたdict形式の検索結果を、
        # APIレスポンス用のDocumentSearchResultへ変換する
        #
        # Service層でレスポンスモデルへ変換しておくことで、
        # Router側ではそのまま返却できる
        results = [
            DocumentSearchResult(
                point_id=result["point_id"],
                score=result["score"],
                text=result["text"],
                source=result["source"],
            )
            for result in search_results
        ]

        # 検索結果全体をAPIレスポンス形式へまとめて返す
        return DocumentSearchResponse(
            success=True,
            query=normalized_query,
            # 実際に取得できた文書数を設定する
            # score_thresholdによってはlimitより少なくなる場合がある
            count=len(results),
            # 類似度の高い文書一覧
            results=results,
        )
