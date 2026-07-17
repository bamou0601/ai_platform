"""
機能: Conversation Message Service
ロジック: Conversation Messageのビジネスロジックを提供する
作成者: 馬 猛
作成日: 2026/7/9
"""

from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.repositories.conversation_message_repository import (
    ConversationMessageRepository,
)
from app.schemas.conversation_message import (
    ConversationMessageCreate,
    ConversationMessageUpdate,
)


class ConversationMessageService:
    """
    Conversation Messageのビジネスロジックを提供するService。

    Conversation Messageの登録、取得、更新、削除などの
    業務処理をRepositoryへ委譲する。
    """

    def __init__(self):
        """
        ConversationMessageServiceを初期化する。

        ConversationMessageRepositoryのインスタンスを生成する。

        Returns:
            None
        """

        self.repository = ConversationMessageRepository()

    def create(
        self, db: Session, data: ConversationMessageCreate
    ) -> ConversationMessage:
        """
        Conversation Messageを登録する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            data (ConversationMessageCreate):
                登録するメッセージ情報

        Returns:
            ConversationMessage:
                登録したConversation Message
        """
        return self.repository.create(db, data)

    def get_all(self, db: Session) -> list[ConversationMessage]:
        """
        すべてのConversation Messageを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

        Returns:
            list[ConversationMessage]:
                Conversation Message一覧
        """
        return self.repository.find_all(db)

    def get(
        self, db: Session, conversation_message_id: int
    ) -> ConversationMessage | None:
        """
        指定したConversation Messageを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_message_id (int):
                Conversation Message ID

        Returns:
            ConversationMessage | None:
                対象のConversation Message。
                存在しない場合はNoneを返す。
        """
        return self.repository.find_by_id(db, conversation_message_id)

    def get_by_conversation(
        self, db: Session, conversation_id: int
    ) -> list[ConversationMessage]:
        """
        指定したConversationのメッセージ一覧を取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_id (int):
                Conversation ID

        Returns:
            list[ConversationMessage]:
                Conversationに属するメッセージ一覧
        """
        return self.repository.find_by_conversation_id(
            db, conversation_id
        )

    def update(
        self,
        db: Session,
        conversation_message_id: int,
        data: ConversationMessageUpdate,
    ) -> ConversationMessage | None:
        """
        Conversation Messageを更新する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_message_id (int):
                更新対象のConversation Message ID
            data (ConversationMessageUpdate):
                更新内容

        Returns:
            ConversationMessage | None:
                更新後のConversation Message。
                対象が存在しない場合はNoneを返す。
        """
        return self.repository.update(
            db, conversation_message_id, data
        )

    def delete(
        self, db: Session, conversation_message_id: int
    ) -> bool:
        """
        Conversation Messageを削除する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            conversation_message_id (int):
                削除対象のConversation Message ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """
        return self.repository.delete(db, conversation_message_id)
