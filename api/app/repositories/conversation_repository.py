"""
機能: Conversation Repository
ロジック: ConversationテーブルへのCRUD操作
creat->find_all->find_by_id->update->deleteという順に
作成者: 馬 猛
作成日: 2026/07/09
"""

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
)


class ConversationRepository:
    """
    Conversationテーブルに対するCRUD処理を提供するRepositoryクラス。
    """

    def create(
        self, db: Session, conversation: ConversationCreate
    ) -> Conversation:
        """
        Conversationを登録する。

        Conversationエンティティを作成し、
        データベースへ保存して登録結果を返却する。

        Args:
            db (Session): データベースセッション
            conversation (ConversationCreate): 登録するConversation情報

        Returns:
            Conversation: 登録したConversation
        """

        # PydanticモデルからORMモデルを生成
        db_conversation = Conversation(
            **conversation.model_dump()
        )

        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)

        return db_conversation

    def find_all(self, db: Session) -> list[Conversation]:
        """
        全てのConversationを取得する。

        Args:
            db (Session): データベースセッション

        Returns:
            list[Conversation]: Conversation一覧
        """

        return db.query(Conversation).all()

    def find_by_id(
        self, db: Session, conversation_id: int
    ) -> Conversation | None:
        """
        指定したIDのConversationを取得する。

        Args:
            db (Session): データベースセッション
            conversation_id (int): Conversation ID

        Returns:
            Conversation | None:
                該当するConversation。
                存在しない場合はNoneを返す。
        """

        return (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def update(
        self,
        db: Session,
        conversation_id: int,
        conversation: ConversationUpdate,
    ) -> Conversation | None:
        """
        Conversationを更新する。

        Args:
            db (Session): データベースセッション
            conversation_id (int): 更新対象のConversation ID
            conversation (ConversationUpdate): 更新内容

        Returns:
            Conversation | None:
                更新後のConversation。
                対象が存在しない場合はNoneを返す。
        """

        # 更新対象を取得
        db_conversation = self.find_by_id(
            db, conversation_id
        )

        if not db_conversation:
            return None

        update_data = conversation.model_dump(
            exclude_unset=True
        )

        # 値を更新
        for key, value in update_data.items():
            setattr(db_conversation, key, value)

        db.commit()
        db.refresh(db_conversation)

        return db_conversation

    def delete(
        self, db: Session, conversation_id: int
    ) -> bool:
        """
        Conversationを削除する。

        Args:
            db (Session): データベースセッション
            conversation_id (int): 削除対象のConversation ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """

        # 削除対象を取得
        db_conversation = self.find_by_id(
            db, conversation_id
        )

        if not db_conversation:
            return False

        # データベースから削除
        db.delete(db_conversation)
        db.commit()

        return True
