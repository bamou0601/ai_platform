
from datetime import datetime
from pydantic import BaseModel

class PromptTemplateCreate(BaseModel):
    name: str

    category: str | None = None

    description: str | None = None

    system_prompt: str

    temperature: float = 0.7

    top_p: float = 0.9

    is_default: bool = False

class PromptTemplateUpdate(BaseModel):

    name: str | None = None

    category: str | None = None

    description: str | None = None

    system_prompt: str | None = None

    temperature: float | None = None

    top_p: float | None = None

    is_default: bool | None = None

class PromptTemplateResponse(BaseModel):

    id: int

    name: str

    category: str | None

    description: str | None

    system_prompt: str

    temperature: float

    top_p: float

    is_default: bool

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }