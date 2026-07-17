"""
機能: Model Repository
ロジック: ModelテーブルへのCRUD操作
作成者: 馬 猛
作成日: 2026/07/10
"""

from sqlalchemy.orm import Session

from app.models.model import Model
from app.schemas.model import ModelCreate, ModelUpdate


class ModelRepository:
    """
    Modelテーブルに対するCRUD処理を提供するRepositoryクラス。
    """

    def create(
        self, db: Session, model: ModelCreate
    ) -> Model:
        """
        Modelを登録する。

        Modelエンティティを作成し、
        データベースへ保存して登録結果を返却する。

        Args:
            db (Session): データベースセッション
            model (ModelCreate): 登録するModel情報

        Returns:
            Model: 登録したModel
        """

        # PydanticモデルからORMモデルを生成
        db_model = Model(**model.model_dump())

        # データベースへ登録
        db.add(db_model)
        db.commit()
        db.refresh(db_model)

        return db_model

    def find_all(self, db: Session) -> list[Model]:
        """
        全てのModelを取得する。

        Args:
            db (Session): データベースセッション

        Returns:
            list[Model]: Model一覧
        """

        return db.query(Model).all()

    def find_by_id(
        self, db: Session, model_id: int
    ) -> Model | None:
        """
        指定したIDのModelを取得する。

        Args:
            db (Session): データベースセッション
            model_id (int): Model ID

        Returns:
            Model | None:
                該当するModel。
                存在しない場合はNoneを返す。
        """

        return (
            db.query(Model)
            .filter(Model.id == model_id)
            .first()
        )

    def update(
        self, db: Session, model_id: int, model: ModelUpdate
    ) -> Model | None:
        """
        Modelを更新する。

        Args:
            db (Session): データベースセッション
            model_id (int): 更新対象のModel ID
            model (ModelUpdate): 更新内容

        Returns:
            Model | None:
                更新後のModel。
                対象が存在しない場合はNoneを返す。
        """
        # 更新対象を取得
        db_model = self.find_by_id(db, model_id)

        if db_model is None:
            return None

        # 更新対象の項目のみ取得
        update_data = model.model_dump(exclude_unset=True)

        # 値を更新
        for key, value in update_data.items():
            setattr(db_model, key, value)

        db.commit()
        db.refresh(db_model)

        return db_model

    def delete(self, db: Session, model_id: int) -> bool:
        """
        Modelを削除する。

        Args:
            db (Session): データベースセッション
            model_id (int): 削除対象のModel ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """

        # 削除対象を取得
        db_model = self.find_by_id(db, model_id)

        if db_model is None:
            return False

        # データベースから削除
        db.delete(db_model)
        db.commit()

        return True
