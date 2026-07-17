"""
機能:Conversation Service
ロジック: Conversationのビジネスロジック
"""

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
)


class ConversationService:
    """
    Conversationのビジネスロジックを提供するService。

    Conversationの登録、取得、更新、削除などの
    業務処理をRepositoryへ委譲する。
    """

    def __init__(self):
        """
        ConversationServiceを初期化する。

        ConversationRepositoryのインスタンスを生成する。

        Returns:
            None
        """
        self.repository = ConversationRepository()

    def create(
        self, db: Session, data: ConversationCreate
    ) -> Conversation:
        """
        Conversationを登録する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            data (ConversationCreate):
                登録するConversation情報

        Returns:
            Conversation:
                登録したConversation
        """
        return self.repository.create(db, data)

    def get_all(self, db: Session) -> list[Conversation]:
        """
        すべてのConversationを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

        Returns:
            list[Conversation]:
                Conversation一覧
        """
        return self.repository.find_all(db)

    def get(
        self, db: Session, conversation_id: int
    ) -> Conversation | None:
        """
        指定したConversationを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_id (int):
                Conversation ID

        Returns:
            Conversation | None:
                対象のConversation。
                存在しない場合はNoneを返す。
        """
        return self.repository.find_by_id(db, conversation_id)

    def update(
        self,
        db: Session,
        conversation_id: int,
        data: ConversationUpdate,
    ) -> Conversation | None:
        """
        Conversationを更新する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_id (int):
                更新対象のConversation ID
            data (ConversationUpdate):
                更新内容

        Returns:
            Conversation | None:
                更新後のConversation。
                対象が存在しない場合はNoneを返す。
        """
        return self.repository.update(db, conversation_id, data)

    def delete(self, db: Session, conversation_id: int) -> bool:
        """
        Conversationを削除する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_id (int):
                削除対象のConversation ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """
        return self.repository.delete(db, conversation_id)
