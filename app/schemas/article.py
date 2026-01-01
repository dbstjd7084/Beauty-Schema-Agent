from .base import BaseSchema
from pydantic import Field
from typing import List

class ArticleSchema(BaseSchema):
    type: str = Field(default="Article", alias="@type")
    headline: str = Field(..., description="기사 제목")
    image: List[str] = Field(..., description="대표 이미지 리스트")
    datePublished: str = Field(..., description="발행일 (ISO 8601 형식)")
    author: dict = Field(..., description="작성자 정보 (type: Person/Organization)")