from typing import List, Optional
from pydantic import Field
from .base import BaseSchema

class ProductSchema(BaseSchema):
    # 기본값으로 Product 설정, JSON 변환 시 @type으로 나감
    type: str = Field(default="Product", alias="@type")
    name: str = Field(..., description="상품명")

    class Config:
        populate_by_name = True