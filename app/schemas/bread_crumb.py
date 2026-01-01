from .base import BaseSchema
from pydantic import Field
from typing import List

class ListItem(BaseSchema):
    type: str = Field(default="ListItem", alias="@type")
    position: int
    name: str
    item: str = Field(..., description="해당 경로의 URL")

class BreadcrumbSchema(BaseSchema):
    type: str = Field(default="BreadcrumbList", alias="@type")
    itemListElement: List[ListItem]