"""
機能: UserテーブルのORMモデル
ロジック: Userごとの操作を管理する
作成者: 馬 猛
作成日: 2026/07/02
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class User(Base):
    """
    ユーザー情報を管理するORMモデル。

    システムを利用するユーザーの基本情報
    (ユーザー名、メールアドレス、作成日時)を管理する。

    Attributes:
        id (int):ユーザーID (主キー)
        name (str):ユーザー名s
        email (str):メールアドレス (一意)
        created_at (datetime):レコード作成日時
    """

    # テーブル名
    __tablename__ = "users"

    # ユーザーID（主キー）
    id = Column(Integer, primary_key=True, index=True)

    # ユーザー名
    name = Column(String(100), nullable=False)

    # メールアドレス（一意）
    email = Column(String(255), unique=True, nullable=False)

    # レコード作成日時
    created_at = Column(DateTime, default=datetime.utcnow)
