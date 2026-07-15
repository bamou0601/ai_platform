# 作成者: 馬 猛
# 作成日: 2026/07/15

from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class PageResponse(
    GenericModel, 
    Generic[T]
):
    total: int
    page: int
    size: int
    items: list[T]

