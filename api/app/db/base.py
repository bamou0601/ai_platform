"""
機能: SQLAlchemy ORM の基底クラス
ロジック: すべてのORMモデルが継承する Base を定義する
作成者: 馬 猛
作成日: 2026/7/6
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    SQLAlchemy ORMのすべてのモデルが継承する基底クラス
    """
    pass