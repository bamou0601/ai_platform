"""
機能: UserテーブルのCRUD処理(業務ロジックを管理するクラス)
ロジック: SQLAlchemyを利用してユーザー情報を操作する
作成者: 馬 猛
作成日: 2026/07/06
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

    def create_user(
        self,
        db: Session,
        user: UserCreate
    ) -> User:
        """ユーザを登録する"""

        return self.repository.create_user(db, user)
    
    def get_users(
            self,
            db: Session
    ) -> list[User]:
        """全ユーザを取得する"""

        return self.repository.find_all(db)
    
    def get_user(
        self,
        db: Session,
        user_id: int
    ) -> User | None:
        """指定したユーザを取得する"""
        return self.repository.find_by_id(
            db,
            user_id
        )
    
    def update_user(
        self,
        db: Session,
        user_id: int,
        user: UserUpdate
    ) -> User | None:
        """ユーザ情報を更新する"""
        return self.repository.update_user(
            db,
            user_id,
            user
        )
    
    def delete_user(
        self,
        db: Session,
        user_id: int
    ) -> bool:
        """ユーザを削除する"""
        return self.repository.delete_user(
            db,
            user_id
        )