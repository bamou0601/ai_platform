"""
機能: Model一覧APIのレスポンススキーマ
ロジック: 利用可能なLLMモデル一覧のレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/7/6
"""

from pydantic import BaseModel


class ModelsResponse(BaseModel):
    """
    Model一覧取得時のレスポンススキーマ。

    APIから返却する利用可能なLLMモデル名の
    一覧を定義する。
    """

    # 利用可能なLLMモデル名の一覧
    models: list[str]
