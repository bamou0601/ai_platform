"""
機能: chat historyテーブルのCRUD処理
ロジック: SQLAlchemyを利用して会話履歴を操作する
作成者: 馬 猛
作成日: 2026/07/07
"""

from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory
from app.schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryUpdate,
)


class ChatHistoryRepository:
    """
    Chat Historyテーブルに対するCRUD処理を提供するRepositoryクラス。
    """

    def create(
        self, db: Session, chat: ChatHistoryCreate
    ) -> ChatHistory:
        """
        会話履歴を登録する。

        ChatHistoryエンティティを作成し、
        データベースへ保存して登録結果を返却する。

        Args:
            db (Session): データベースセッション
            chat (ChatHistoryCreate): 登録する会話履歴情報

        Returns:
            ChatHistory: 登録した会話履歴
        """

        # PydanticモデルからORMモデルを生成
        db_chat = ChatHistory(**chat.model_dump())

        # データベースへ登録
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)

        return db_chat

    def find_all(self, db: Session) -> list[ChatHistory]:
        """
        全ての会話履歴を取得する。

        Args:
            db (Session): データベースセッション

        Returns:
            list[ChatHistory]: 会話履歴一覧
        """

        return db.query(ChatHistory).all()

    def find_by_id(
        self, db: Session, chat_id: int
    ) -> ChatHistory | None:
        """
        指定したIDの会話履歴を取得する。

        Args:
            db (Session): データベースセッション
            chat_id (int): 会話履歴ID

        Returns:
            ChatHistory | None:
                該当する会話履歴。
                存在しない場合はNoneを返す。
        """

        return (
            db.query(ChatHistory)
            .filter(ChatHistory.id == chat_id)
            .first()
        )

    def update(
        self,
        db: Session,
        chat_id: int,
        chat: ChatHistoryUpdate,
    ) -> ChatHistory | None:
        """
        会話履歴を更新する。

        Args:
            db (Session): データベースセッション
            chat_id (int): 更新対象の会話履歴ID
            chat (ChatHistoryUpdate): 更新内容

        Returns:
            ChatHistory | None:
                更新後の会話履歴。
                対象が存在しない場合はNoneを返す。
        """

        # 更新対象を取得
        db_chat = (
            db.query(ChatHistory)
            .filter(ChatHistory.id == chat_id)
            .first()
        )

        if db_chat is None:
            return None

        # 更新対象の項目のみ取得
        update_data = chat.model_dump(exclude_unset=True)

        # 値を更新
        for key, value in update_data.items():
            setattr(db_chat, key, value)

        db.commit()
        db.refresh(db_chat)

        return db_chat

    def delete(self, db: Session, chat_id: int) -> bool:
        """
        会話履歴を削除する。

        Args:
            db (Session): データベースセッション
            chat_id (int): 削除対象の会話履歴ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """

        # 削除対象を取得
        db_chat = (
            db.query(ChatHistory)
            .filter(ChatHistory.id == chat_id)
            .first()
        )

        if db_chat is None:
            return False

        # データベースから削除
        db.delete(db_chat)
        db.commit()

        return True
