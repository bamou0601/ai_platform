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
    PromptTemplateResponse,
    PromptTemplatePage
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
    #response_model=list[PromptTemplateResponse]
    response_model=PromptTemplatePage
)
def get_prompts(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    active: bool | None = None,
    sort: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    return service.get_all(
        db, page, size, keyword, active, sort, order
    )


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

# 有効一覧
@router.get(
    "/active",
    response_model=list[PromptTemplateResponse]
)
def get_active(
    db: Session = Depends(get_db)
):
    return service.get_active(db)


# Default Prompt
@router.get(
    "/default",
    response_model=PromptTemplateResponse
)
def get_default(
    db: Session = Depends(get_db)
):
    return service.get_default(db)


# 有効化
@router.patch(
    "/{prompt_id}/enable",
    response_model=PromptTemplateResponse
)
def enable(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    return service.enable(
        db,
        prompt_id
    )

# 無効化
@router.patch(
    "/{prompt_id}/disable",
    response_model=PromptTemplateResponse
)
def disable(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    return service.disable(
        db,
        prompt_id
    )

# Default変更
@router.patch(
    "/{prompt_id}/default",
    response_model=PromptTemplateResponse
)
def set_default(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    return service.set_default(
        db,
        prompt_id
    )

