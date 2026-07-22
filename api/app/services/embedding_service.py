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

        self.embed_url = (
            f"{settings.ollama_url.rstrip('/')}/api/embed"
        )
        self.model = settings.embedding_model
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

        normalized_text = text.strip()

        if not normalized_text:
            raise ValueError("Embedding対象のテキストが空です。")

        payload: dict[str, any] = {
            "model": self.model,
            "input": normalized_text,
        }

        logger.info(
            "Calling Ollama embedding API. model=%s",
            self.model,
        )

        response = requests.post(
            self.embed_url,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        response_data = response.json()
        embeddings = response_data.get("embeddings")

        if not embeddings or not isinstance(embeddings, list):
            raise ValueError(
                "OllamaからEmbeddingが返されませんでした。"
            )

        embedding = embeddings[0]

        if not isinstance(embedding, list):
            raise ValueError("Embeddingのレスポンス形式が不正です。")

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

        actual_dimension = len(embedding)

        if actual_dimension != self.expected_dimension:
            raise ValueError(
                "Embeddingの次元数がQdrant設定と一致しません。"
                f" expected={self.expected_dimension},"
                f" actual={actual_dimension}"
            )
