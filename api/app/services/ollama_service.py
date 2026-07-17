"""
機能: Ollama Service
ロジック: Ollama APIとの通信およびモデル情報の取得を行う
作成者: 馬 猛
作成日: 2026/07/02
"""

import logging

import requests

from app.config import settings

logger = logging.getLogger(__name__)


# Ollama とのやり取りを担当するサービスクラス
class OllamaService:
    """
    Ollamaとの通信を行うService。

    Ollama APIへチャットリクエストを送信し、
    AIからの応答や利用可能なモデル一覧を取得する。
    """

    # ユーザーからのメッセージを受け取り、応答を返す
    def chat(self, messages: list[dict]) -> str:
        """
        Ollamaへチャットリクエストを送信する。

        会話履歴を含むメッセージをOllama APIへ送信し、
        AIが生成した回答を取得する。

        Args:
            messages (list[dict]):
                Ollamaへ送信する会話メッセージ一覧

        Returns:
            str:
                AIが生成した回答
        """

        # ログの設定を初期化
        logger.info("Calling ollama...")
        # ログにモデル名を出力
        logger.info(f"Model: {settings.ollama_model}")
        logger.info(f"User Message: {messages}")

        response = requests.post(
            f"{settings.ollama_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )

        # リクエストの内容をログに出力
        logger.info(f"Request: {response.request.body}")

        # 応答のステータスコードを確認し、エラーがあれば例外を発生させる
        response.raise_for_status()
        data = response.json()

        # 応答の内容をログに出力
        # logger.info(f"System Prompt: {system_prompt}")

        logger.info("Response received from Ollama.")

        answer = data["message"]["content"]
        # 応答データを ChatResponse 型に変換して返す
        logger.info(f"Response: {answer}")

        return answer

    def get_models(self):
        """
        利用可能なOllamaモデル一覧を取得する。

        Ollama APIの/api/tagsを呼び出し、
        利用可能なモデル名のみを一覧で取得する。

        Returns:
            list[str]:
                利用可能なモデル名一覧
        """

        response = requests.get(
            f"{settings.ollama_url}/api/tags", timeout=30
        )

        # 成功ステータスでなければ例外を発生させる
        response.raise_for_status()

        data = response.json()

        models = [model["name"] for model in data.get("models", [])]

        logger.info(f"Available Models5: {models}")

        return models
