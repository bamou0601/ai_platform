"""
機能: Model Service
ロジック: Modelのビジネスロジック
作成者: 馬 猛
作成日: 2026/07/10
修正日: 2026/07/21
"""

import time

from sqlalchemy.orm import Session

from app.llm.base import LLMService
from app.llm.ollama import OllamaService
from app.models.model import Model
from app.repositories.model_repository import (
    ModelRepository,
)
from app.schemas.model import ModelCreate, ModelUpdate
from app.schemas.openai import ModelListResponse, ModelObject


class ModelService:
    """
    Modelのビジネスロジックを提供するService。

    Modelの登録、取得、更新、削除などの
    業務処理をRepositoryへ委譲する。
    """

    def __init__(self):
        """
        ModelServiceを初期化する。

        ModelRepositoryおよびLLMServiceの
        インスタンスを生成する。

        Returns:
            None
        """

        # Model Repositoryを生成
        self.repository = ModelRepository()

        # LLM抽象型としてOllama実装を設定
        self.llm_service: LLMService = OllamaService()

    def create(self, db: Session, data: ModelCreate) -> Model:
        """
        Modelを登録する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            data (ModelCreate):
                登録するModel情報

        Returns:
            Model:
                登録したModel
        """
        return self.repository.create(db, data)

    def get_all(self, db: Session) -> list[Model]:
        """
        すべてのModelを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション

        Returns:
            list[Model]:
                Model一覧
        """
        return self.repository.find_all(db)

    def get(self, db: Session, model_id: int) -> Model | None:
        """
        指定したModelを取得する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            model_id (int):
                Model ID

        Returns:
            Model | None:
                対象のModel。
                存在しない場合はNoneを返す。
        """
        return self.repository.find_by_id(db, model_id)

    def update(
        self, db: Session, model_id: int, data: ModelUpdate
    ) -> Model | None:
        """
        Modelを更新する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            model_id (int):
                更新対象のModel ID
            data (ModelUpdate):
                更新内容

        Returns:
            Model | None:
                更新後のModel。
                対象が存在しない場合はNoneを返す。
        """
        return self.repository.update(db, model_id, data)

    def delete(self, db: Session, model_id: int) -> bool:
        """
        Modelを削除する。

        Args:
            db (Session):
                SQLAlchemyのデータベースセッション
            model_id (int):
                削除対象のModel ID

        Returns:
            bool:
                削除成功時はTrue、
                対象が存在しない場合はFalseを返す。
        """
        return self.repository.delete(db, model_id)

    def get_models(self) -> ModelListResponse:
        """
        利用可能なLLMモデル一覧を取得する。

        LLMプロバイダーから利用可能なモデル名一覧を取得し、
        OpenAI互換のモデル一覧レスポンスへ変換する。

        Returns:
            ModelListResponse:
                OpenAI互換のモデル一覧レスポンス
        """

        # LLMプロバイダーからモデル名一覧を取得
        model_names = self.llm_service.get_models()

        # モデル名をOpenAI互換モデル情報へ変換
        models = [
            ModelObject(
                id=model_name,
                # object="model",
                created=int(time.time()),
                owned_by="ollama",
            )
            for model_name in model_names
        ]

        # OpenAI互換モデル一覧レスポンスを返却
        return ModelListResponse(
            # object="list",
            data=models,
        )
