"""
機能: UserテーブルのRepository(SQLを書く場所)
ロジック: SQLAlchemyを利用してデータアクセスを行う
作成者: 馬 猛
作成日: 2026/07/07
"""
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    """
    Userテーブルのデータアクセスを提供するRepository
    """
    def create(
            self,
            db: Session,
            user: UserCreate
    ) -> User:
        """ユーザを登録する"""
 
        db_user = User(**user.model_dump())

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    
    def find_all(
            self,
            db: Session
    ) -> list[User]:
        """
        全ユーザを取得する
        """
        return db.query(User).all()
    
    def find_by_id(
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
    
    def update(
            self,
            db: Session,
            user_id: int,
            user: UserUpdate
    ) -> User | None:
        """
        ユーザ情報を更新する
        """

        db_user = self.find_by_id(
            db, 
            User.id == user_id
        )

        if db_user is None:
            return None
        
        update_data = user.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                db_user,
                key,
                value
            )

        db.commit()
        db.refresh(db_user)

        return db_user
    
    def delete(
            self,
            db: Session,
            user_id: int
    ) -> bool:
        """
        ユーザを削除する
        """
    
        db_user = self.find_by_id(
            db, 
            User.id == user_id
        )
    
        if db_user is None:
            return False
    
        db.delete(db_user)
        db.commit()
        return True