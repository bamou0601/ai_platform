"""
機能: Chat Historyのビジネスロジック
ロジック: Repositoryを利用して会話履歴を操作する
作成者: 馬 猛
作成日: 2026/07/07
"""

from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory
from app.repositories.chat_history_repository import (
    ChatHistoryRepository,
)
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryUpdate,
)


class ChatHistoryService:
    """
    Chat Historyに関するビジネスロジックを提供するServiceクラス。

    Repositoryを利用して会話履歴の登録、取得、更新、
    削除などの業務処理を実行する。
    """

    def __init__(self):
        """
        ChatHistoryServiceを初期化する。

        ChatHistoryRepositoryのインスタンスを生成し、
        CRUD処理で利用する。

        Returns:
            None
        """
        self.repository = ChatHistoryRepository()

    def create_chat(
        self, db: Session, chat: ChatHistoryCreate
    ) -> ChatHistory:
        """
        会話履歴を登録する。

        Args:
            db (Session): SQLAlchemyのデータベースセッション
            chat (ChatHistoryCreate): 登録する会話履歴情報

        Returns:
            ChatHistory: 登録した会話履歴
        """

        return self.repository.create(db, chat)

    def get_chats(self, db: Session) -> list[ChatHistory]:
        """
        全会話履歴を取得する。

        Args:
            db (Session): SQLAlchemyのデータベースセッション

        Returns:
            list[ChatHistory]: 会話履歴一覧
        """

        return self.repository.find_all(db)

    def get_chat(
        self, db: Session, chat_id: int
    ) -> ChatHistory | None:
        """
        指定した会話履歴を取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            chat_id (int):
                会話履歴ID

        Returns:
            ChatHistory | None:
                対象の会話履歴。
                存在しない場合はNoneを返す。
        """

        return self.repository.find_by_id(db, chat_id)

    def update_chat(
        self,
        db: Session,
        chat_id: int,
        chat: ChatHistoryUpdate,
    ) -> ChatHistory | None:
        """
        会話履歴を更新する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            chat_id (int):
                更新対象の会話履歴ID
            chat (ChatHistoryUpdate):
                更新内容

        Returns:
            ChatHistory | None:
                更新後の会話履歴。
                対象が存在しない場合はNoneを返す。
        """

        return self.repository.update(db, chat_id, chat)

    def delete_chat(self, db: Session, chat_id: int) -> bool:
        """
        会話履歴を削除する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            chat_id (int):
                削除対象の会話履歴ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """

        return self.repository.delete(db, chat_id)
