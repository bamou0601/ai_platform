"""
機能: Embedding生成サービス
ロジック: Ollama APIを利用してテキストからEmbeddingベクトルを生成する
作成者: 馬 猛
作成日: 2026/07/22
"""

import logging
from typing import Any

import requests

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Ollamaを利用してEmbeddingを生成する。"""

    def __init__(self) -> None:
        """Embedding APIの接続情報を初期化する。"""

        # OllamaのEmbedding API URLを生成する
        #
        # rstrip("/")を使用することで、
        # OLLAMA_URLの末尾に「/」があっても
        # 「//api/embed」にならないようにする
        #
        # 例:
        # http://127.0.0.1:11434/
        # ↓
        # http://127.0.0.1:11434/api/embed
        self.embed_url = (
            f"{settings.ollama_url.rstrip('/')}/api/embed"
        )

        # Embedding生成に使用するモデル名を設定する
        # 現在は.envでbge-m3を指定している
        self.model = settings.embedding_model

        # Qdrant Collectionで使用する
        # Embeddingベクトルの想定次元数を設定する
        # bge-m3の場合は1024次元
        self.expected_dimension = settings.embedding_dimension

    def embed(self, text: str) -> list[float]:
        """
        テキストからEmbeddingベクトルを生成する。

        Args:
            text: Embeddingへ変換するテキスト

        Returns:
            list[float]: 生成されたEmbeddingベクトル

        Raises:
            ValueError: 入力テキストまたはレスポンスが不正な場合
            requests.RequestException: Ollamaとの通信に失敗した場合
        """

        # 入力文章の前後にある不要な空白や改行を削除する
        normalized_text = text.strip()

        # 空白を削除した結果、文章が空になった場合は
        # Embeddingを生成できないためエラーにする
        if not normalized_text:
            raise ValueError("Embedding対象のテキストが空です。")

        # Ollamaの/api/embedへ送信するリクエストデータを作成する
        #
        # model:
        #   Embedding生成に使用するモデル
        #
        # input:
        #   Embeddingへ変換する元の文章
        payload: dict[str, Any] = {
            "model": self.model,
            "input": normalized_text,
        }

        logger.info(
            "Calling Ollama embedding API. model=%s",
            self.model,
        )

        # OllamaへPOSTリクエストを送信し、
        # テキストからEmbeddingベクトルを生成する
        #
        # timeout=60を指定することで、
        # 60秒以内に応答がない場合は通信エラーとして扱う
        response = requests.post(
            self.embed_url,
            json=payload,
            timeout=60,
        )

        # HTTPステータスが4xxまたは5xxの場合は、
        # requests側で例外を発生させる
        #
        # 200系の場合はそのまま次の処理へ進む
        response.raise_for_status()

        # Ollamaから返されたJSONレスポンスを
        # Pythonのdictへ変換する
        response_data = response.json()

        # Ollamaのレスポンスから
        # Embedding一覧を取得する
        embeddings = response_data.get("embeddings")

        # embeddingsが存在しない場合、
        # またはlist形式でない場合は、
        # Ollamaから想定したレスポンスが返っていないためエラーにする
        if not embeddings or not isinstance(embeddings, list):
            raise ValueError(
                "OllamaからEmbeddingが返されませんでした。"
            )

        # /api/embedは複数文章にも対応しているため、
        # embeddingsは「ベクトルの一覧」として返される
        #
        # 今回は1つの文章だけ送信しているので、
        # 最初のEmbeddingベクトルを取得する
        embedding = embeddings[0]

        # 取得したEmbeddingがlist形式でない場合は、
        # 想定したベクトル形式ではないためエラーにする
        if not isinstance(embedding, list):
            raise ValueError("Embeddingのレスポンス形式が不正です。")

        # 生成されたベクトルの次元数が、
        # Qdrant Collectionの設定と一致しているか確認する
        self._validate_dimension(embedding)

        logger.info(
            "Embedding generated. model=%s dimension=%d",
            self.model,
            len(embedding),
        )

        return embedding

    def _validate_dimension(
        self,
        embedding: list[float],
    ) -> None:
        """
        Embeddingの次元数を検証する。

        Args:
            embedding: 検証対象のEmbeddingベクトル

        Raises:
            ValueError: 想定した次元数と一致しない場合
        """
        # 実際に生成されたEmbeddingベクトルの要素数を取得する
        actual_dimension = len(embedding)

        # Qdrant Collection作成時に指定した次元数と、
        # Embeddingモデルが生成した実際の次元数を比較する
        #
        # 例:
        # Qdrant Collection = 1024次元
        # Embedding          = 768次元
        #
        # この状態ではQdrantへ登録・検索できないため、
        # Repositoryへ渡す前にエラーとして検出する
        if actual_dimension != self.expected_dimension:
            raise ValueError(
                "Embeddingの次元数がQdrant設定と一致しません。"
                f" expected={self.expected_dimension},"
                f" actual={actual_dimension}"
            )
