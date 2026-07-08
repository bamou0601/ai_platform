"""
機能: Prompt Template API
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse
)

from app.services.prompt_template_service import (
    PromptTemplateService
)

router = APIRouter(
    prefix="/prompt-templates",
    tags=["Prompt Templates"]
)

service = PromptTemplateService()


@router.post(
    "",
    response_model=PromptTemplateResponse
)
def create_prompt(
    prompt: PromptTemplateCreate,
    db: Session = Depends(get_db)
):
    return service.create_prompt(
        db,
        prompt
    )


@router.get(
    "",
    response_model=list[PromptTemplateResponse]
)
def get_prompts(
    db: Session = Depends(get_db)
):
    return service.get_prompts(db)


@router.get(
    "/{prompt_id}",
    response_model=PromptTemplateResponse
)
def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):

    prompt = service.get_prompt(
        db,
        prompt_id
    )

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    return prompt


@router.put(
    "/{prompt_id}",
    response_model=PromptTemplateResponse
)
def update_prompt(
    prompt_id: int,
    request: PromptTemplateUpdate,
    db: Session = Depends(get_db)
):

    prompt = service.update_prompt(
        db,
        prompt_id,
        request
    )

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    return prompt


@router.delete(
    "/{prompt_id}"
)
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):

    success = service.delete_prompt(
        db,
        prompt_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found"
        )

    return {
        "message": "Prompt deleted successfully"
    }