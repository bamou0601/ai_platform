"""
機能: Chat History APIのエンドポイント
ロジック: ChatHistoryServiceを呼び出しCRUD APIを提供する
作成者: 馬 猛
作成日: 2026/07/07
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryResponse,
    ChatHistoryUpdate,
)
from app.services.chat_history_service import ChatHistoryService

router = APIRouter(prefix="/chat-history", tags=["Chat History"])

service = ChatHistoryService()


@router.post("", response_model=ChatHistoryResponse)
def create_chat(
    chat: ChatHistoryCreate, db: Session = Depends(get_db)
):
    """
    会話履歴を登録する
    """

    return service.create_chat(db, chat)


@router.get("", response_model=list[ChatHistoryResponse])
def get_chats(db: Session = Depends(get_db)):
    """
    全会話履歴を取得する
    """

    return service.get_chats(db)


@router.get("/{chat_id}", response_model=ChatHistoryResponse)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    """
    指定した会話履歴を取得する
    """

    chat = service.get_chat(db, chat_id)

    if chat is None:
        raise HTTPException(
            status_code=404, detail="Chat history not found"
        )

    return chat


@router.put("/{chat_id}", response_model=ChatHistoryResponse)
def update_chat(
    chat_id: int,
    chat: ChatHistoryUpdate,
    db: Session = Depends(get_db),
):
    """
    会話履歴を更新する
    """

    db_chat = service.update_chat(db, chat_id, chat)

    if db_chat is None:
        raise HTTPException(
            status_code=404, detail="Chat history not found"
        )

    return db_chat


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    """
    会話履歴を削除する
    """

    success = service.delete_chat(db, chat_id)

    if not success:
        raise HTTPException(
            status_code=404, detail="Chat history not found"
        )

    return {"message": "Chat history deleted successfully"}
