# """
# 機能: チャット API のリクエスト/レスポンス型
# ロジック: Pydantic モデルとして入力と出力の構造を定義する
# 作成者: 馬 猛
# 作成日: 2026/07/2
# """

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """チャットリクエストの入力データ構造""" 
    user_id: int
    message: str

class ChatResponse(BaseModel):
    """チャットレスポンスの出力データ構造"""
    answer: str