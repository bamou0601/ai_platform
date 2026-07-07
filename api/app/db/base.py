# 
# 機能: SQLAlchemy ORM の基底クラス
# ロジック: すべてのORMモデルが継承する Base を定義する
# 
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    SQLAlchemy ORMのすべてのモデルが継承する基底クラス
    """
    pass