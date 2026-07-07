"""
機能: データベースの初期化
ロジック: ORMモデルからテーブルを作成する
"""

from app.db.base import Base
from app.db.database import engine

# Userモデルを読み込む
import app.models

def init_db():
    """ORMモデルからテーブルを作成する"""
    Base.metadata.create_all(bind=engine)