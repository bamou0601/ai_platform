"""
機能: SQLAlchemyセッション管理
ロジック: SQLAlchemyのセッションファクトリーを生成し、データベースセッションを作成できるようにする
作成者: 馬 猛
作成日: 2026/7/6
"""

from sqlalchemy.orm import sessionmaker
from app.db.database import engine

# SQLAlchemyのセッションファクトリーを作成
# get_db()から呼び出され、リクエストごとにデータベースセッションを生成する
SessionLocal = sessionmaker(
    bind=engine,        # 接続先のデータベースエンジン
    autoflush=False,    # commit()するまで自動でDBへ反映しない
    autocommit=False    # commit()を明示的に呼び出すまでトランザクションを確定しない
)