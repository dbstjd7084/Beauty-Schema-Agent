from .base import BaseSchema
from pydantic import Field
from typing import Optional


class LocalBusinessSchema(BaseSchema):
    type: str = Field(default="LocalBusiness", alias="@type")
    name: str = Field(..., description="매장명")
    address: dict = Field(..., description="주소 정보 (streetAddress, addressLocality 등)")
    telephone: Optional[str] = Field(None, description="전화번호")
    priceRange: Optional[str] = Field(None, description="가격대 (예: ₩₩)")