"""
機能: Modelテーブル
ロジック: 利用可能なLLMモデルを管理する
作成者: 馬 猛
作成日: 2026/07/10
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from app.db.base import Base


class Model(Base):
    """
    利用可能なLLMモデルを管理するORMモデル。

    モデル名、プロバイダー、バージョン情報、および
    利用可否などの情報をデータベースへ保存する。

    Attributes:
        id (int): モデルID(主キー)
        name (str): モデル名
        provider (str): モデル提供元
        version (str): モデルのバージョン
        is_active (bool): 利用可否
        created_at (datetime): 登録日時
    """

    # テーブル名
    __tablename__ = "models"

    # モデルID（主キー）
    id = Column(Integer, primary_key=True, index=True)

    # モデル名（一意）
    name = Column(String(100), nullable=False, unique=True)

    # モデル提供元（Ollama、OpenAIなど）
    provider = Column(String(100), nullable=False)

    # モデルのバージョン
    version = Column(String(50))

    # 利用可否
    is_active = Column(Boolean, default=True)

    # 登録日時
    created_at = Column(DateTime, default=datetime.utcnow)
