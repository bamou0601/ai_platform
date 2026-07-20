"""
機能: OpenAI互換性Chat Completions API スキーマ
ロジック: OpenAI APIと互換性のあるリクエスト・レスポンスを定義する
メソッドの順番:Message,ChatCompletionRequest,Usage,Choice
ChatCompletionResponse,ModelObject,ModelListResponse
作成者: 馬 猛
作成日: 2026/07/20
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    """
    Chat Message

    OpenAI Chat Completions APIで使用する
    メッセージ形式を定義する。
    """

    # メッセージ送信者
    role: Literal["system", "user", "assistant", "tool"]
    # メッセージ内容
    content: str


class ChatCompletionRequest(BaseModel):
    """
    Chat Completion リクエスト

    OpenAI Chat Completions APIと互換性のある
    入力データを定義する。
    """

    # 使用するモデル
    model: str
    # 会話履歴
    messages: list[Message]
    # ランダム性
    temperature: float = Field(default=0.7, ge=0, le=2)
    # Top-p Sampling
    top_p: float = Field(default=1.0, ge=0, le=1)
    # 最大生成トークン数
    max_tokens: int = Field(default=1024, gt=0)
    # 同じ話題を繰り返さないようにする
    presence_penalty: float = Field(default=0.0, ge=-2, le=2)
    # 同じ単語の繰り返しを減らす
    frequency_penalty: float = Field(default=0.0, ge=-2, le=2)
    # 停止文字列
    stop: list[str] | None = None
    # 再現性向上用
    seed: int | None = None
    # ユーザー識別子
    user: str | None = None
    # ストリーミング有無
    stream: bool = False


class Usage(BaseModel):
    """
    Token使用量
    API利用時のトークン数を保持する。
    """

    # 入力トークン数
    prompt_tokens: int
    # 出力トークン数
    completion_tokens: int
    # 合計トークン数
    total_tokens: int


class Choice(BaseModel):
    """
    AI応答

    Chat Completionで生成された
    応答情報を保持する。
    """

    # 応答番号
    index: int
    # AI応答メッセージ
    message: Message
    # 応答終了理由
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    """
    Chat Completion レスポンス

    OpenAI互換レスポンスを定義する。
    """

    # レスポンスID
    id: str
    # オブジェクト種別
    object: str = "chat.completion"
    # 作成時刻（Unix Time）
    created: int
    # 使用したモデル
    model: str
    # 応答一覧
    choices: list[Choice]
    # トークン使用量
    usage: Usage

    model_config = ConfigDict(from_attributes=True)


# Model一覧API
class ModelObject(BaseModel):
    """
    モデル情報

    利用可能なLLM情報を保持する。
    """

    # モデルID
    id: str
    # オブジェクト種別
    object: str = "model"
    # 登録時刻（Unix Time）
    created: int
    # 提供元
    owned_by: str


class ModelListResponse(BaseModel):
    """
    モデル一覧レスポンス

    OpenAI互換のモデル一覧を返却する。
    """

    # オブジェクト種別
    object: str = "list"
    # モデル一覧
    data: list[ModelObject]
