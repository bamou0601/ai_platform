"""
機能: LLM Serviceの抽象クラス
ロジック: 各LLMサービス共通のインターフェースを定義する
作成者: 馬 猛
作成日: 2026/07/20
"""

from abc import ABC, abstractclassmethod


class LLMService(ABC):
    """
    LLMサービスの抽象クラス
    """

    @abstractclassmethod
    def chat(self, messages: list[dict]) -> str:
        """
        チャットを実行する。

        Args:
            messages: 会話履歴

        Returns: AI応答
        """
        pass

    @abstractclassmethod
    def get_models(self) -> list[str]:
        """
        利用可能モデル一覧を取得する。

        Returns:
            モデル一覧
        """
        pass
