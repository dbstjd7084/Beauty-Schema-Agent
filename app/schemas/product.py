from typing import List, Optional
from pydantic import Field
from .base import BaseSchema

class ProductSchema(BaseSchema):
    type: str = Field(default="Product", alias="@type")
    name: str = Field(..., description="상품명")

    class Config:
        populate_by_name = True