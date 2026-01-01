from .base import BaseSchema
from pydantic import Field
from typing import Optional

class VideoSchema(BaseSchema):
    type: str = Field(default="VideoObject", alias="@type")
    name: str = Field(..., description="영상 제목")
    description: str = Field(..., description="영상 설명")
    thumbnailUrl: str = Field(..., description="썸네일 URL")
    uploadDate: str = Field(..., description="업로드 날짜")
    contentUrl: Optional[str] = Field(None, description="영상 실제 파일 URL")