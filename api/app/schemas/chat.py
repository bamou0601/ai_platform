# """
# 機能: チャット API のリクエスト/レスポンス型
# ロジック: Pydantic モデルとして入力と出力の構造を定義する
# 作成者: 馬 猛
# 作成日: 2026/07/10
# """

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    チャットリクエスト

    ユーザーから送信されるチャット内容と、
    利用するプロンプトテンプレートおよび
    会話情報を受け取るリクエストスキーマ。
    """

    user_id: int

    # 新規会話ならNone
    conversation_id: int | None = None

    message: str
    prompt_template_id: int


class ChatResponse(BaseModel):
    """
    チャットレスポンス

    AIから生成された回答と、
    対応する会話IDを返却するレスポンススキーマ。
    """

    conversation_id: int
    answer: str
