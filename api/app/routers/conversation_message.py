from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.conversation_message import *

from app.services.conversation_message_service import ConversationMessageService


router = APIRouter(
    prefix="/conversation_messages",
    tags=["Conversation Messages"]
)

service = ConversationMessageService()


@router.post(
    "",
    response_model=ConversationMessageResponse
)
def create(
    request: ConversationMessageCreate,
    db: Session = Depends(get_db)
):
    return service.create(
        db,
        request
    )


@router.get(
    "",
    response_model=list[ConversationMessageResponse]
)
def get_all(
    db: Session = Depends(get_db)
):
    return service.get_all(db)


@router.get(
    "/{id}",
    response_model=ConversationMessageResponse
)
def get(
    id: int,
    db: Session = Depends(get_db)
):
    return service.get(
        db,
        id
    )


@router.put(
    "/{id}",
    response_model=ConversationMessageResponse
)
def update(
    id: int,
    request: ConversationMessageUpdate,
    db: Session = Depends(get_db)
):
    return service.update(
        db,
        id,
        request
    )


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db)
):
    service.delete(db,id)
    
    return {
        "message": "deleted"
    }