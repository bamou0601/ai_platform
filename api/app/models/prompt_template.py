"""
機能: Prompt Templateテーブル
ロジック: AIプロンプトテンプレートを管理する
作成者: 馬 猛
作成日: 2026/07/08
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.db.base import Base


class PromptTemplate(Base):
    """
    AIプロンプトテンプレートを管理するORMモデル。

    システムプロンプトや推論パラメータ(Temperature、Top P)、
    テンプレートの分類、デフォルト設定、利用可否などの情報を
    データベースへ保存する。

    Attributes:
        id (int): テンプレートID(主キー)
        name (str): テンプレート名
        category (str): テンプレートのカテゴリ
        description (str): テンプレートの説明
        system_prompt (str): システムプロンプト
        temperature (float): Temperature値
        top_p (float): Top P値
        is_default (bool): デフォルトテンプレートかどうか
        is_active (bool): 利用可否
        created_at (datetime): 登録日時
        updated_at (datetime): 更新日時
    """

    # テーブル名
    __tablename__ = "prompt_templates"

    # テンプレートID（主キー）
    id = Column(Integer, primary_key=True, index=True)

    # テンプレート名
    name = Column(String(100), nullable=False)

    # テンプレートのカテゴリ
    category = Column(String(50))

    # テンプレートの説明
    description = Column(Text)

    # システムプロンプト
    system_prompt = Column(Text, nullable=False)

    # Temperature（応答のランダム性）
    temperature = Column(Float, default=0.7)

    # Top P（確率上位から選択する割合）
    top_p = Column(Float, default=0.9)

    # デフォルトテンプレートかどうか
    is_default = Column(Boolean, default=False)

    # 利用可否
    is_active = Column(
        Boolean, nullable=False, default=True
    )

    # 登録日時
    created_at = Column(DateTime, default=datetime.utcnow)

    # 更新日時
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
