# """
# 機能: Ollama サービス連携
# ロジック: リクエストを Ollama API に送信し、応答を ChatResponse へ整形する
# 作成者: 馬 猛
# 作成日: 2026/07/2
# """

import requests 
from app.schemas.chat import ChatResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Ollama とのやり取りを担当するサービスクラス
class OllamaService:
    # ユーザーからのメッセージを受け取り、応答を返す
    def chat(
            self, 
            messages: list[dict]
    ) -> str:

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
                "stream": False
            },
            timeout=120
        )

        # リクエストの内容をログに出力
        logger.info(f"Request: {response.request.body}")

        # 応答のステータスコードを確認し、エラーがあれば例外を発生させる
        response.raise_for_status()
        data = response.json()

        # 応答の内容をログに出力
        # logger.info(f"System Prompt: {system_prompt}")
        
        logger.info("Response received from Ollama.")

        answer=data["message"]["content"]
        # 応答データを ChatResponse 型に変換して返す
        logger.info(f"Response: {answer}")
        
        return answer
    
    def get_models(self):
        # """Ollama サーバーから利用可能なモデル（タグ）一覧を取得する。

        # 処理の流れ:
        # 1. 設定された `settings.ollama_url` に対して `/api/tags` へ GET リクエストを送信する。
        # 2. HTTP レスポンスのステータスコードをチェックし、成功でなければ例外を送出する。
        # 3. レスポンスのボディを JSON としてパースし、そのデータを返す。

        # 戻り値:
        #     dict|list: Ollama API が返す JSON データ（モデル/タグ一覧）。
        # """

        # API へ GET リクエストを送信

        logger = logging.getLogger(__name__)
        
        response = requests.get(
            f"{settings.ollama_url}/api/tags",
            timeout=30
        )

         # 成功ステータスでなければ例外を発生させる
        response.raise_for_status()
               
        data = response.json()

        models = [
            model["name"]
            for model in data.get("models", [])
        ]

        logger.info(f"Available Models5: {models}")

        return models


