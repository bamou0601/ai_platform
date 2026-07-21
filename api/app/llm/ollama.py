"""
機能: Ollama Service
ロジック: OpenAI互換リクエストをOllama APIへ送信し、
         Ollamaの応答をOpenAI互換レスポンスへ変換する
作成者: 馬 猛
作成日: 2026/07/20
修正日: 2026/07/21
"""

import json
import logging
import time
import uuid
from collections.abc import Iterator

import requests

from app.config import settings
from app.llm.base import LLMService
from app.schemas.openai import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    Message,
    Usage,
)

logger = logging.getLogger(__name__)


# Ollama とのやり取りを担当するサービスクラス
class OllamaService(LLMService):
    """
    Ollama APIとの通信を担当するLLMサービス。

    OpenAI互換のChatCompletionRequestをOllama形式へ変換して送信し、
    Ollamaから取得した応答をChatCompletionResponseへ変換する。
    """

    # ユーザーからのメッセージを受け取り、応答を返す
    def chat(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Ollamaへチャットリクエストを送信する。

        OpenAI互換リクエストをOllama APIの形式へ変換して送信し、
        取得した回答、終了理由、およびトークン使用量を
        OpenAI互換レスポンスとして返却する。

        Args:
            request (ChatCompletionRequest):
                OpenAI互換のチャットリクエスト

        Returns:
            ChatCompletionResponse:
                OpenAI互換のチャットレスポンス

        Raises:
            ValueError:
                ストリーミングが指定された場合
            requests.exceptions.RequestException:
                Ollama APIとの通信に失敗した場合
        """
        # 非ストリーミングのみ対応
        if request.stream:
            raise ValueError("Streaming is not supported yet.")

        # PydanticモデルをOllamaのメッセージ形式へ変換
        messages = [
            message.model_dump(exclude_none=True)
            for message in request.messages
        ]

        # Ollamaへ渡す推論オプションを生成
        options = {
            "temperature": request.temperature,
            "top_p": request.top_p,
            "num_predict": request.max_tokens,
        }

        # seedが指定されている場合のみ追加
        if request.seed is not None:
            options["seed"] = request.seed

        # 停止文字列が指定されている場合のみ追加
        if request.stop:
            options["stop"] = request.stop

        # ollamaへ送信するリクエストを生成
        payload = {
            "model": request.model,
            "messages": messages,
            "stream": False,
            "options": options,
        }

        # ログの設定を初期化
        logger.info("Calling Ollama...")
        logger.info("Model: %s", request.model)

        # Ollama Chat APIを呼び出す
        response = requests.post(
            f"{settings.ollama_url}/api/chat",
            json=payload,
            timeout=120,
        )

        # HTTPエラーが発生した場合は例外送出
        response.raise_for_status()

        # OllamaのJSONレスポンスを取得
        data = response.json()

        # AI回答を取得
        answer = data.get("message", {}).get("content", "")

        # 入力トークン数を所得
        prompt_tokens = data.get("prompt_eval_count", 0)

        # 出力トークン数を取得
        completion_tokens = data.get("eval_count", 0)

        # トークン使用量を生成
        usage = Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=(prompt_tokens + completion_tokens),
        )

        # AI回答情報を生成
        choice = Choice(
            index=0,
            message=Message(
                role="assistant",
                content=answer,
            ),
            finish_reason=data.get("done_reason", "stop"),
        )

        # OpenAI互換レスポンスを生成
        chat_response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex}",
            object="chat.completion",
            created=int(time.time()),
            model=data.get("model", request.model),
            choices=[choice],
            usage=usage,
        )

        logger.info("Response received from Ollama.")
        logger.info("Prompt tokens: %s", prompt_tokens)
        logger.info("Completion tokens: %s", completion_tokens)

        return chat_response

    def chat_stream(
        self,
        request: ChatCompletionRequest,
    ) -> Iterator[str]:
        """
        Ollamaを使用してストリーミングチャットを実行する。

        OllamaのNDJSONレスポンスを読み込み、
        OpenAI互換のSSE形式へ変換して返却する。

        Args:
            request (ChatCompletionRequest):
                OpenAI互換チャットリクエスト

        Returns:
            Iterator[str]:
                OpenAI互換SSEレスポンス
        """

        # レスポンス共通情報を生成
        completion_id = f"chatcmpl-{uuid.uuid4().hex}"
        created = int(time.time())

        # Ollama向けリクエストを生成
        payload = {
            "model": request.model,
            "messages": [
                message.model_dump() for message in request.messages
            ],
            "stream": True,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "num_predict": request.max_tokens,
                "presence_penalty": request.presence_penalty,
                "frequency_penalty": request.frequency_penalty,
                "seed": request.seed,
                "stop": request.stop,
            },
        }

        # None値を除外
        payload["options"] = {
            key: value
            for key, value in payload["options"].items()
            if value is not None
        }

        logger.info("Calling Ollama streaming API...")
        logger.info("Model: %s", request.model)

        try:
            # Ollamaへストリーミングリクエストを送信
            with requests.post(
                f"{settings.ollama_url}/api/chat",
                json=payload,
                stream=True,
                timeout=(10, None),
            ) as response:
                response.raise_for_status()

                # assistantロールを最初のチャンクとして返却
                role_chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                            },
                            "finish_reason": None,
                        }
                    ],
                }

                yield self._format_sse(role_chunk)

                # OllamaのNDJSONを1行ずつ処理
                for line in response.iter_lines(
                    decode_unicode=True,
                ):
                    if not line:
                        continue

                    ollama_chunk = json.loads(line)

                    # 生成途中のテキストを取得
                    content = ollama_chunk.get("message", {}).get(
                        "content", ""
                    )

                    if content:
                        content_chunk = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": request.model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "content": content,
                                    },
                                    "finish_reason": None,
                                }
                            ],
                        }

                        yield self._format_sse(content_chunk)

                    # Ollamaの生成完了を処理
                    if ollama_chunk.get("done", False):
                        finish_reason = self._convert_finish_reason(
                            ollama_chunk.get("done_reason"),
                        )

                        finish_chunk = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": request.model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {},
                                    "finish_reason": finish_reason,
                                }
                            ],
                        }

                        yield self._format_sse(finish_chunk)

                        logger.info(
                            "Streaming response completed.",
                        )

                        break

                # OpenAI互換の終了通知
                yield "data: [DONE]\n\n"

        except requests.exceptions.RequestException:
            logger.exception(
                "Failed to call Ollama streaming API.",
            )
            raise

        except json.JSONDecodeError:
            logger.exception(
                "Failed to parse Ollama streaming response.",
            )
            raise

    @staticmethod
    def _format_sse(data: dict) -> str:
        """
        辞書データをSSE形式へ変換する。

        Args:
            data (dict): SSEとして返却するデータ

        Returns:
            str: SSE形式の文字列
        """

        json_data = json.dumps(
            data,
            ensure_ascii=False,
        )

        return f"data: {json_data}\n\n"

    @staticmethod
    def _convert_finish_reason(
        done_reason: str | None,
    ) -> str:
        """
        Ollamaの終了理由をOpenAI互換形式へ変換する。

        Args:
            done_reason (str | None): OllamaのOllamaの終了理由

        Returns:
            str: OpenAI互換の終了理由
        """

        if done_reason == "length":
            return "length"

        return "stop"

    def get_models(self) -> list[str]:
        """
        利用可能なOllamaモデル一覧を取得する。

        Ollama APIの/api/tagsを呼び出し、
        登録されているモデル名のみを一覧として返却する。

        Returns:
            list[str]:
                利用可能なOllamaモデル名一覧

        Raises:
            requests.exceptions.RequestException:
                Ollama APIとの通信に失敗した場合
        """

        # Ollamaのモデル一覧APIを呼び出す
        response = requests.get(
            f"{settings.ollama_url}/api/tags", timeout=30
        )

        # 成功ステータスでなければ例外を発生させる
        response.raise_for_status()

        # OllamaのJSONレスポンスを取得
        data = response.json()

        # モデル名のみを抽出
        models = [model["name"] for model in data.get("models", [])]

        logger.info("Available models: %s", models)

        return models
