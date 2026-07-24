"""
機能: データベースセッションの提供
ロジック: リクエストごとにSessionを生成し、処理後に自動でクローズする
作成者: 馬 猛
作成日: 2026/7/6
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得する。

    FastAPIのDependency Injection(Depends)で利用するための
    データベースセッションを生成する。リクエスト処理中は
    同一セッションを利用し、処理終了後は必ずセッションを
    クローズしてリソースを解放する。

    Yields:
        Session: SQLAlchemyのデータベースセッション

    Returns:
        None
    """

    # データベースセッションを生成
    db = SessionLocal()
    try:
        # 呼び出し元へデータベースセッションを返却
        yield db
    finally:
        # 処理終了後にデータベースセッションをクローズ
        db.close()
