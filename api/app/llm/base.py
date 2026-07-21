"""
機能: LLM Serviceの抽象クラス
ロジック: 各LLMサービス共通のインターフェースを定義する
作成者: 馬 猛
作成日: 2026/07/20
修正日: 2026/07/21
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from app.schemas.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)


class LLMService(ABC):
    """
    LLMプロバイダー共通の抽象クラス。

    チャット実行とモデル一覧取得の
    共通インターフェースを定義する。
    """

    @abstractmethod
    def chat(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        チャットを実行する。

        Args:
            request (ChatCompletionRequest):
                OpenAI互換のチャットリクエスト

        Returns:
            ChatCompletionResponse:
                OpenAI互換のチャットレスポンス
        """

        raise NotImplementedError

    @abstractmethod
    def chat_stream(
        self,
        request: ChatCompletionRequest,
    ) -> Iterator[str]:
        """
        ストリーミング形式でチャットを実行する。

        Args:
            request (ChatCompletionRequest):
                OpenAI互換チャットリクエスト

        Returns:
            Iterator[str]:
                OpenAI互換SSEレスポンス
        """
        raise NotImplementedError

    @abstractmethod
    def get_models(self) -> list[str]:
        """
        利用可能なモデル一覧を取得する。

        Returns:
            list[str]:
                利用可能なモデル名一覧
        """
        raise NotImplementedError
