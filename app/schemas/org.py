from .base import BaseSchema
from pydantic import Field
from typing import List

class OrganizationSchema(BaseSchema):
    type: str = Field(default="Organization", alias="@type")
    name: str = Field(..., description="브랜드/기업명")
    url: str = Field(..., description="공식 홈페이지 URL")
    logo: str = Field(..., description="로고 이미지 URL")
    sameAs: List[str] = Field(default=[], description="공식 소셜 미디어 리스트")