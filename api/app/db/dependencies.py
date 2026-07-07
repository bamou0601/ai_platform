"""
機能: データベースセッションの提供
ロジック: リクエストごとにSessionを生成し、処理後に自動でクローズする
"""
from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    リクエストごとにDBセッションを生成し、
     処理終了後に自動でクローズする。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()