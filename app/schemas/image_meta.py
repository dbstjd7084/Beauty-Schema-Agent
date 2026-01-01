from .base import BaseSchema
from pydantic import Field

class ImageMetadataSchema(BaseSchema):
    type: str = Field(default="ImageObject", alias="@type")
    contentUrl: str = Field(..., description="이미지 원본 URL")
    license: str = Field(..., description="라이선스 정보 페이지 URL")
    acquireLicensePage: str = Field(..., description="라이선스 획득 페이지 URL")