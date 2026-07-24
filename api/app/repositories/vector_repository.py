"""
機能: ベクトルデータ操作
ロジック: QdrantのCollection操作を管理する
作成者: 馬 猛
作成日: 2026/07/22
"""

import logging
from typing import Any

from qdrant_client.models import (
    Distance,
    PointStruct,
    UpdateStatus,
    VectorParams,
)

from app.config import settings
from app.vector.qdrant_client import QdrantVectorClient

logger = logging.getLogger(__name__)


class VectorRepository:
    """Qdrantのベクトルデータ操作を管理する。"""

    def __init__(self) -> None:
        """QdrantClientを初期化する。"""

        # Qdrantとの通信に使用するClientを取得する
        self.client = QdrantVectorClient().get_client()

    def create_collection(self) -> bool:
        """
        Collectionが存在しない場合に作成する。

        Returns:
            bool: 新規作成した場合はTrue、
                すでに存在する場合はFalse
        """
        # Qdrantに現在存在しているCollection一覧を取得する
        collections = self.client.get_collections()

        # Collectionオブジェクトから名前だけを取り出し、
        # 存在確認しやすいリストへ変換する
        names = [
            collection.name for collection in collections.collections
        ]

        # 同じ名前のCollectionがすでに存在する場合は、
        # 重複して作成する必要がないため処理を終了する
        if settings.qdrant_collection in names:
            return False

        # Collectionが存在しない場合だけ新規作成する
        #
        # size:
        #   Embeddingモデルが生成するベクトルの次元数を指定する
        #
        # COSINE:
        #   ベクトル同士の向きの近さを使って類似度を計算する
        self.client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimension,
                distance=Distance.COSINE,
            ),
        )

        return True

    def upsert_document(
        self,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """
        文書ベクトルとPayloadをQdrantへ登録する。

        Args:
            point_id: Qdrantへ登録するPoint ID
            vector: 文書から生成したEmbeddingベクトル
            payload: 文書情報を保持するPayload

        Raises:
            ValueError: 入力値またはUpsert結果が不正な場合
            RuntimeError: Qdrantへの登録に失敗した場合
        """

        # Point IDが空の場合は、
        # Qdrant上でデータを一意に識別できないためエラーにする
        if not point_id:
            raise ValueError("Point ID must not be empty.")

        # Embeddingベクトルが空の場合は、
        # Qdrantへベクトルデータとして登録できないためエラーにする
        if not vector:
            raise ValueError("Vector must not be empty.")

        # Qdrant Collection作成時に指定した次元数と、
        # 実際に登録するEmbeddingベクトルの次元数が
        # 一致しているか確認する
        #
        # 例:
        # Collection = 1024次元
        # vector     = 768次元
        #
        # この場合はQdrantへ登録できないため、
        # API呼び出し前にエラーとして検出する
        if len(vector) != settings.embedding_dimension:
            raise ValueError(
                "Vector dimension does not match the configured "
                "embedding dimension. "
                f"expected={settings.embedding_dimension}, "
                f"actual={len(vector)}"
            )

        # Payloadには元の文章やsourceなど、
        # 検索後に利用する情報を保存するため、
        # 空の場合は登録対象として不正と判断する
        if not payload:
            raise ValueError("Payload must not be empty.")

        try:
            logger.info(
                "Upserting document into Qdrant. "
                "collection=%s point_id=%s dimension=%d",
                settings.qdrant_collection,
                point_id,
                len(vector),
            )

            # QdrantへPointを登録する
            #
            # Pointは主に以下の情報を持つ
            # - id      : データを識別するID
            # - vector  : 類似検索に使用するEmbedding
            # - payload : 元文章やsourceなどの付加情報
            #
            # upsertは、
            # 同じIDがなければ新規登録、
            # 同じIDがあれば更新として動作する
            result = self.client.upsert(
                collection_name=settings.qdrant_collection,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                ],
                # Qdrant側の登録処理が完了するまで待ってから
                # 結果を返す
                wait=True,
            )

        except Exception as exception:
            # Qdrantへの通信失敗や登録処理エラーが発生した場合、
            # 元の例外内容をスタックトレース付きでログへ出力する
            logger.exception(
                "Failed to upsert document into Qdrant. "
                "collection=%s point_id=%s",
                settings.qdrant_collection,
                point_id,
            )

            # Repository内部の詳細な例外をそのまま上位へ渡さず、
            # アプリケーション側で扱いやすいRuntimeErrorへ変換する
            raise RuntimeError(
                "Failed to upsert the document into Qdrant."
            ) from exception

        # Qdrant APIの呼び出し自体が成功していても、
        # 登録処理が正常完了していない可能性があるため
        # UpdateStatusを確認する
        if result.status != UpdateStatus.COMPLETED:
            raise RuntimeError(
                "Qdrant upsert operation was not completed. "
                f"status={result.status}"
            )

        logger.info(
            "Document was successfully upserted into Qdrant. "
            "collection=%s point_id=%s",
            settings.qdrant_collection,
            point_id,
        )

    def search_similar(
        self,
        vector: list[float],
        limit: int,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        指定されたベクトルに類似する文書を検索する。

        Args:
            vector: 検索テキストから生成したEmbeddingベクトル
            limit: 取得する検索結果の最大件数
            score_threshold: 検索結果に含める最低類似度

        Returns:
            list[dict[str, Any]]: 類似文書の検索結果

        Raises:
            ValueError: 検索条件が不正な場合
            RuntimeError: Qdrantでの検索に失敗した場合
        """

        # 検索用ベクトルが空の場合は、
        # Qdrantで類似度を計算できないためエラーにする
        if not vector:
            raise ValueError("Search vector must not be empty.")

        # 検索時も登録時と同様に、
        # Collectionのベクトル次元数と一致している必要がある
        if len(vector) != settings.embedding_dimension:
            raise ValueError(
                "Search vector dimension does not match the configured "
                "embedding dimension. "
                f"expected={settings.embedding_dimension}, "
                f"actual={len(vector)}"
            )

        # limitが0以下だと取得する検索結果数として不正なため、
        # Qdrantへリクエストする前にエラーにする
        if limit < 1:
            raise ValueError(
                "Search result limit must be greater than zero."
            )

        try:
            logger.info(
                "Searching similar documents in Qdrant. "
                "collection=%s limit=%d score_threshold=%s",
                settings.qdrant_collection,
                limit,
                score_threshold,
            )

            # Qdrantへ類似検索を実行する
            #
            # query:
            #   検索対象となるEmbeddingベクトル
            #
            # limit:
            #   類似度が高い順に取得する最大件数
            #
            # score_threshold:
            #   指定された類似度以上のデータだけを返す
            #
            # with_payload=True:
            #   vectorだけでなく、登録時に保存した
            #   textやsourceも検索結果として取得する
            #
            # with_vectors=False:
            #   1024次元のEmbeddingベクトル自体は
            #   APIレスポンスとして不要なため取得しない
            response = self.client.query_points(
                collection_name=settings.qdrant_collection,
                query=vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

        except Exception as exception:
            # Qdrantへの接続失敗や検索処理で例外が発生した場合、
            # 詳細なスタックトレースをログへ記録する
            logger.exception(
                "Failed to search similar documents in Qdrant. "
                "collection=%s",
                settings.qdrant_collection,
            )

            raise RuntimeError(
                "Failed to search similar documents in Qdrant."
            ) from exception

        # Qdrant独自のレスポンス形式を、
        # Service層で扱いやすいdict形式へ変換する
        results: list[dict[str, Any]] = []

        # Qdrantから返されたPointを1件ずつ処理する
        for point in response.points:
            # PayloadがNoneの場合でも後続処理でエラーにならないよう、
            # 空のdictを初期値として使用する
            payload = point.payload or {}

            # Service層ではQdrant固有のPointオブジェクトへ
            # 依存しないよう、必要な値だけをdictへ詰め替える
            results.append(
                {
                    # Qdrant上のPoint ID
                    "point_id": str(point.id),
                    # 検索ベクトルとの類似度
                    "score": float(point.score),
                    # 登録時にPayloadへ保存した元の文章
                    # textが存在しない場合は空文字を使用する
                    "text": str(payload.get("text", "")),
                    # 文書の取得元
                    # sourceが登録されていない場合はNoneになる
                    "source": payload.get("source"),
                }
            )
        logger.info(
            "Similar document search completed. "
            "collection=%s result_count=%d",
            settings.qdrant_collection,
            len(results),
        )

        return results
