"""
機能: Ollamaモデル一覧API
ロジック: Ollamaから利用可能なモデル一覧を取得するAPIを提供する
作成者: 馬 猛
作成日: 2026/7/3
"""

from fastapi import APIRouter

from app.llm.ollama import OllamaService
from app.schemas.models import ModelsResponse

router = APIRouter(prefix="/models", tags=["Models"])

service = OllamaService()


@router.get("", response_model=ModelsResponse)
def get_models():
    return ModelsResponse(models=service.get_models())
