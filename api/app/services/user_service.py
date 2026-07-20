"""
機能: UserテーブルのCRUD処理(業務ロジックを管理するクラス)
ロジック: SQLAlchemyを利用してユーザー情報を操作する
作成者: 馬 猛
作成日: 2026/7/6
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Userテーブルに対する業務ロジックを提供するサービス"""

    def __init__(self):
        """Repositoryを初期化する"""
        self.repository = UserRepository()

    def create(self, db: Session, data: UserCreate) -> User:
        """ユーザを登録する"""

        return self.repository.create(db, data)

    def get_all(self, db: Session) -> list[User]:
        """全ユーザを取得する"""

        return self.repository.find_all(db)

    def get(self, db: Session, user_id: int) -> User | None:
        """指定したユーザを取得する"""
        return self.repository.find_by_id(db, user_id)

    def update(
        self, db: Session, user_id: int, data: UserUpdate
    ) -> User | None:
        """ユーザ情報を更新する"""
        return self.repository.update(db, user_id, data)

    def delete(self, db: Session, user_id: int) -> bool:
        """ユーザを削除する"""
        return self.repository.delete(db, user_id)
