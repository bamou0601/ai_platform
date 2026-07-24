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

        # レスポンス全体で共通して使用するIDと作成時刻を生成する
        # ストリーミング中に返す複数のチャンクでも、
        # 同じcompletion_idとcreatedを使用する
        completion_id = f"chatcmpl-{uuid.uuid4().hex}"
        created = int(time.time())

        # OpenAI互換リクエストをOllama向けの形式へ変換する
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

        # Ollamaへ不要なNone値を送信しないため、
        # 値が設定されているオプションだけを残す
        payload["options"] = {
            key: value
            for key, value in payload["options"].items()
            if value is not None
        }

        logger.info("Calling Ollama streaming API...")
        logger.info("Model: %s", request.model)

        try:
            # Ollamaへストリーミングリクエストを送信する
            # stream=Trueを指定することで、
            # 回答完了まで待たずに生成途中のデータを順次受信できる
            with requests.post(
                f"{settings.ollama_url}/api/chat",
                json=payload,
                stream=True,
                timeout=(10, None),
            ) as response:
                # HTTPステータスが4xxまたは5xxの場合は例外を発生させる
                # 正常な200系レスポンスの場合はそのまま次の処理へ進む
                response.raise_for_status()

                # OpenAI互換のストリーミングでは、
                # 最初にassistantロールだけを通知するチャンクを返す
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

                # Ollamaは生成途中のレスポンスを
                # NDJSON形式で1行ずつ返すため、
                # 受信した行を順番に処理する
                for line in response.iter_lines(
                    decode_unicode=True,
                ):
                    # 空行の場合は処理対象のデータが存在しないため、
                    # JSON変換を行わず次の行へ進む
                    if not line:
                        continue

                    # 1行分のJSON文字列をPythonのdictへ変換する
                    ollama_chunk = json.loads(line)

                    # Ollamaレスポンスのmessage.contentから、
                    # 今回新しく生成されたテキスト部分を取得する
                    #
                    # messageやcontentが存在しない場合でも
                    # エラーにならないように空文字を初期値として使用する
                    content = ollama_chunk.get("message", {}).get(
                        "content", ""
                    )

                    # contentが空文字でない場合だけ、
                    # OpenAI互換のストリーミングチャンクとして返却する
                    #
                    # Ollamaは生成完了通知など、
                    # contentを持たないレスポンスを返す場合もあるため、
                    # その場合はテキストチャンクを生成しない
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

                        # Pythonのyieldを使用することで、
                        # すべての回答生成が完了するまで待たずに
                        # Open WebUIへ少しずつ回答を返す
                        yield self._format_sse(content_chunk)

                    # done=Trueは、
                    # Ollama側で回答生成が完了したことを表す
                    #
                    # done=Falseの場合はまだ生成途中なので、
                    # 次のNDJSONレスポンスを待つ
                    if ollama_chunk.get("done", False):
                        # Ollama独自の終了理由を
                        # OpenAI互換のfinish_reasonへ変換する
                        #
                        # 例:
                        # "stop"   → "stop"
                        # "length" → "length"
                        finish_reason = self._convert_finish_reason(
                            ollama_chunk.get("done_reason"),
                        )

                        # 回答本文ではなく、
                        # 「生成処理が終了した」ことを通知する
                        # 最後のチャンクを作成する
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

                        # done=Trueになった時点でOllamaの回答生成は終了しているため、
                        # これ以上レスポンスを読み続ける必要がない
                        # forループを終了する
                        break

                # OpenAI互換ストリーミングでは、
                # 最後に[DONE]を送信して、
                # クライアントへストリーム終了を通知する
                yield "data: [DONE]\n\n"

        except requests.exceptions.RequestException:
            # Ollamaへの接続失敗、タイムアウト、
            # HTTPエラーなどの通信関連例外を処理する
            logger.exception(
                "Failed to call Ollama streaming API.",
            )
            raise

        except json.JSONDecodeError:
            # Ollamaから受信した1行が正しいJSON形式でない場合に処理する
            # 想定外のレスポンス形式や破損データの調査に利用する
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
        # Pythonの辞書データをJSON文字列へ変換する
        # ensure_ascii=Falseを指定することで、
        # 日本語をUnicodeエスケープせず、そのまま出力する
        json_data = json.dumps(
            data,
            ensure_ascii=False,
        )

        # SSEでは各データの先頭に「data: 」を付け、
        # 最後に空行（改行2つ）を入れて1つのイベントとして送信する
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

        # 最大トークン数に到達して生成が終了した場合は、
        # OpenAI互換形式の「length」を返す
        if done_reason == "length":
            return "length"

        # 通常終了や終了理由が取得できない場合は、
        # OpenAI互換形式の「stop」として扱う
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
