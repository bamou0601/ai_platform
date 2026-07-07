"""
機能: UserテーブルのCRUD処理
ロジック: SQLAlchemyを利用してユーザー情報を操作する
作成者: 馬 猛
作成日: 2026/07/06
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    """
    Userテーブルに対するCRUDを提供するサービス
    """

    def create_user(
            self,
            db: Session,
            user: UserCreate
    ) -> User:
        """ユーザを登録する"""

        db_user = User(
            name=user.name,
            email=user.email
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    
    def get_users(
            self,
            db: Session
    ) -> list[User]:
        """
        全ユーザを取得する
        """
        return db.query(User).all()
    
    def get_user(
            self,
            db: Session,
            user_id: int
    ) -> User | None:
        """
        指定したユーザを取得する
        """
        
        return(
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    
    def update_user(
            self,
            db: Session,
            user_id: int,
            user: UserUpdate
    ) -> User | None:
        """
        ユーザ情報を更新する
        """

        db_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if db_user is None:
            return None
        
        db_user.name = user.name
        db_user.email = user.email

        db.commit()
        db.refresh(db_user)

        return db_user
    
    def delete_user(
            self,
            db: Session,
            user_id: int
    ) -> bool:
        """
        ユーザを削除する
        """
    
        db_user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    
        if db_user is None:
            return False
    
        db.delete(db_user)
        db.commit()
        return True