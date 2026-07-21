"""
機能: Conversation API
ロジック: Conversationに対するCRUD APIを提供する
作成者: 馬 猛
作成日: 2026/7/9
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversation"])

service = ConversationService()


@router.post("", response_model=ConversationResponse)
def create(
    request: ConversationCreate, db: Session = Depends(get_db)
):
    return service.create(db, request)


@router.get("", response_model=list[ConversationResponse])
def get_all(db: Session = Depends(get_db)):
    return service.get_all(db)


@router.get("/{id}", response_model=ConversationResponse)
def get(id: int, db: Session = Depends(get_db)):
    return service.get(db, id)


@router.put("/{id}", response_model=ConversationResponse)
def update(
    id: int,
    request: ConversationUpdate,
    db: Session = Depends(get_db),
):
    return service.update(db, id, request)


@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    service.delete(db, id)

    return {"message": "deleted"}
