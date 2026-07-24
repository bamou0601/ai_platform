"""
機能: データベース接続設定
ロジック: PostgreSQL 接続用の URL を生成し、SQLAlchemy の Engine を作成する
作成者: 馬 猛
作成日: 2026/07/06
"""

from sqlalchemy import create_engine

from app.config import settings

# PostgreSQL 接続用の URL を生成
DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:"
    f"{settings.postgres_password}@"
    f"{settings.postgres_host}:"
    f"{settings.postgres_port}/"
    f"{settings.postgres_db}"
)

# SQLAlchemy の Engine を作成
# Engine はデータベースとの接続管理や SQL 実行の入り口となるオブジェクト
engine = create_engine(
    DATABASE_URL,
    # 実行される SQL をログに出力（開発・デバッグ用）
    echo=True,
)
