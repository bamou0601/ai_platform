from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.model import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
)
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["Model"])

service = ModelService()


@router.post("", response_model=ModelResponse)
def create(request: ModelCreate, db: Session = Depends(get_db)):
    return service.create(db, request)


@router.get("", response_model=list[ModelResponse])
def get_all(db: Session = Depends(get_db)):
    return service.get_all(db)


@router.get("/{id}", response_model=ModelResponse)
def get(id: int, db: Session = Depends(get_db)):
    return service.get(db, id)


@router.put("/{id}", response_model=ModelResponse)
def update(
    id: int,
    request: ModelUpdate,
    db: Session = Depends(get_db),
):
    return service.update(db, id, request)


@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    service.delete(db, id)

    return {"message": "deleted"}
