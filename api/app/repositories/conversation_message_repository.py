"""
機能: Conversation Message Repository
ロジック: Conversation_MessagesテーブルへのCRUD操作
作成者: 馬 猛
作成日: 2026/07/09
"""

from sqlalchemy.orm import Session

from app.models.conversation_message import (
    ConversationMessage,
)
from app.schemas.conversation_message import (
    ConversationMessageCreate,
    ConversationMessageUpdate,
)


class ConversationMessageRepository:
    """
    Conversation Messageテーブルに対するCRUD処理を提供するRepositoryクラス。
    """

    def create(
        self,
        db: Session,
        conversation_message: ConversationMessageCreate,
    ) -> ConversationMessage:
        """
        Conversation Messageを登録する。

        ConversationMessageエンティティを作成し、
        データベースへ保存して登録結果を返却する。

        Args:
            db (Session): データベースセッション
            conversation_message (ConversationMessageCreate):
                登録するメッセージ情報

        Returns:
            ConversationMessage: 登録したメッセージ
        """
        # PydanticモデルからORMモデルを生成
        db_conversation_message = ConversationMessage(
            **conversation_message.model_dump()
        )

        # データベースへ登録
        db.add(db_conversation_message)
        db.commit()
        db.refresh(db_conversation_message)

        return db_conversation_message

    def find_all(
        self, db: Session
    ) -> list[ConversationMessage]:
        """
        全てのConversation Messageを取得する。

        Args:
            db (Session): データベースセッション

        Returns:
            list[ConversationMessage]: メッセージ一覧
        """

        return db.query(ConversationMessage).all()

    def find_by_id(
        self, db: Session, conversation_message_id: int
    ) -> ConversationMessage | None:
        """
        指定したIDのConversation Messageを取得する。

        Args:
            db (Session): データベースセッション
            conversation_message_id (int): メッセージID

        Returns:
            ConversationMessage | None:
                該当するメッセージ。
                存在しない場合はNoneを返す。
        """

        return (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.id
                == conversation_message_id
            )
            .first()
        )

    def find_by_conversation_id(
        self, db: Session, conversation_id: int
    ) -> list[ConversationMessage]:
        """
        指定したConversationに属するメッセージ一覧を取得する。

        作成日時の昇順で取得する。

        Args:
            db (Session): データベースセッション
            conversation_id (int): Conversation ID

        Returns:
            list[ConversationMessage]:
                Conversationに属するメッセージ一覧
        """

        return (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.conversation_id
                == conversation_id
            )
            .order_by(ConversationMessage.created_at)
            .all()
        )

    def update(
        self,
        db: Session,
        conversation_message_id: int,
        conversation_message: ConversationMessageUpdate,
    ) -> ConversationMessage | None:
        """
        Conversation Messageを更新する。

        Args:
            db (Session): データベースセッション
            conversation_message_id (int): 更新対象のメッセージID
            conversation_message (ConversationMessageUpdate):
                更新内容

        Returns:
            ConversationMessage | None:
                更新後のメッセージ。
                対象が存在しない場合はNoneを返す。
        """

        # 更新対象を取得
        db_conversation_message = self.find_by_id(
            db, conversation_message_id
        )

        if not db_conversation_message:
            return None

        # 更新対象の項目のみ取得
        update_data = conversation_message.model_dump(
            exclude_unset=True
        )

        # 値を更新
        for key, value in update_data.items():
            setattr(db_conversation_message, key, value)

        db.commit()
        db.refresh(db_conversation_message)

        return db_conversation_message

    def delete(
        self, db: Session, conversation_message_id: int
    ) -> bool:
        """
        Conversation Messageを削除する。

        Args:
            db (Session): データベースセッション
            conversation_message_id (int): 削除対象のメッセージID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """
        # 削除対象を取得
        db_conversation_message = self.find_by_id(
            db, conversation_message_id
        )

        if not db_conversation_message:
            return False

        # データベースから削除
        db.delete(db_conversation_message)
        db.commit()

        return True
