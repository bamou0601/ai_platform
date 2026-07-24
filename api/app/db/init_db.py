"""
機能: データベースの初期化
ロジック: ORMモデルからテーブルを作成する
作成者: 馬 猛
作成日: 2026/07/06
"""

from app.db.base import Base
from app.db.database import engine


# ORM モデルを読み込む
# モデルを読み込むことで Base.metadata にテーブル情報が登録される
def init_db():
    """ORMモデルからテーブルを作成する"""
    Base.metadata.create_all(bind=engine)
