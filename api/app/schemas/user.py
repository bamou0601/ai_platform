"""
機能: User APIのリクエスト・レスポンススキーマ
ロジック: Pydanticで入力値の検証とレスポンス形式を定義する
作成者: 馬 猛
作成日: 2026/07/02
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    """
    ユーザー登録時のリクエストスキーマ

    クライアントから送信される
    名前とメールアドレスを受け取る。
    """
    name: str
    email: str

class UserUpdate(BaseModel):
    """
    ユーザー更新時のリクエストスキーマ

    指定したユーザーの
    名前とメールアドレスを更新する。
    """
    name: str
    email: str

class UserResponse(BaseModel):
    """
    ユーザー情報取得時のレスポンススキーマ
    APIから返却する
    ユーザー情報を定義する。
    """
    id: int
    name: str
    email: str
    created_at: datetime

    # SQLAlchemy ORMオブジェクトから
    # Pydanticモデルへ変換できるようにする
    model_config = ConfigDict(from_attributes=True)