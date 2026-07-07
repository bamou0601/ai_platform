"""
機能: User APIのエンドポイント
ロジック: UserServiceを呼び出しCRUD APIを提供する
作成者: 馬 猛
作成日: 2026/07/07
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

service = UserService()

@router.post("", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """ユーザを登録する"""
    return service.create_user(db, user)


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db)
):
    """全ユーザを取得する"""
    return service.get_users(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """指定したユーザを取得する"""
    user = service.get_user(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found "
        )
    
    return user

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    """ユーザ情報を更新する"""
    db_user = service.update_user(
        db,
        user_id,
        user
    )

    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return db_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """ユーザを削除する"""
    success = service.delete_user(
        db,
        user_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="User not found"  
        )
    
    return{
        "message": "User deleted successfully"
    }
