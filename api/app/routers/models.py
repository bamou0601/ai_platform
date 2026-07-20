from fastapi import APIRouter

from app.schemas.models import ModelsResponse
from app.services.ollama_service import OllamaService

router = APIRouter(prefix="/models", tags=["Models"])

service = OllamaService()


@router.get("", response_model=ModelsResponse)
def get_models():
    return ModelsResponse(models=service.get_models())
