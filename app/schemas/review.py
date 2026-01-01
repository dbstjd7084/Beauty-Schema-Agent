from .base import BaseSchema
from pydantic import Field

class ReviewSchema(BaseSchema):
    type: str = Field(default="Review", alias="@type")
    author: str = Field(..., description="리뷰 작성자 이름")
    reviewBody: str = Field(..., description="리뷰 본문 내용")
    reviewRating: dict = Field(..., description="별점 정보 (ratingValue 포함)")
    itemReviewed: dict = Field(..., description="리뷰 대상 상품 정보")