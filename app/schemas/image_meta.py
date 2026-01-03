from .base import BaseSchema
from pydantic import Field

# target_schema_name = current_task["type"]
# entity_name = current_task["name"]

prompt = """
당신은 **target_schema_name SEO 구조화 데이터 전문가**입니다.
대상은 **entity_name**이며, 이를 기반으로 마크업을 생성하세요.

[지침]:
해당 대상과 관련된 유효한 정보만 `application/ld+json` 스크립트 형식으로 추출하세요.

[필수 속성]:
- contentUrl: 이미지 콘텐츠의 URL입니다.
- creator, creditText, copyrightNotice, license 중 하나 이상의 라이선스 관련 속성을 포함하세요.

[권장 속성]:
- acquireLicensePage: 이미지 라이선스를 획득할 수 있는 페이지의 URL입니다.
- creator: Organization 또는 Person 형태로 이미지의 제작자 정보를 포함합니다.
    - creator.name: 제작자의 전체 이름을 정확히 기재하세요.
- creditText: 이미지에 대한 크레딧 정보를 포함합니다.
- copyrightNotice: 이미지의 저작권 정보를 포함합니다.
- license: 이미지의 라이선스 정보 페이지 URL을 기재하세요.

[출력 예시]:
{
    "@context": "https://schema.org/",
    "@type": "ImageObject",
    "contentUrl": "https://example.com/photos/1x1/black-labrador-puppy.jpg",
    "license": "https://example.com/license",
    "acquireLicensePage": "https://example.com/how-to-use-my-images",
    "creditText": "Labrador PhotoLab",
    "creator": {
    "@type": "Person",
    "name": "Brixton Brownstone"
    },
    "copyrightNotice": "Clara Kent"
},
{
    "@context": "https://schema.org/",
    "@type": "ImageObject",
    "contentUrl": "https://example.com/photos/1x1/adult-black-labrador.jpg",
    "license": "https://example.com/license",
    "acquireLicensePage": "https://example.com/how-to-use-my-images",
    "creditText": "Labrador PhotoLab",
    "creator": {
    "@type": "Person",
    "name": "Brixton Brownstone"
    },
    "copyrightNotice": "Clara Kent"
}
"""

class ImageMetaSchema(BaseSchema):
    type: str = Field(default="ImageObject", alias="@type")
    contentUrl: str = Field(..., description="이미지 원본 URL")
    creator: dict = Field(default=None, description="이미지 제작자 정보 (type: Person/Organization)")
    creditText: str = Field(default=None, description="이미지 크레딧 정보")
    copyrightNotice: str = Field(default=None, description="이미지 저작권 정보")
    license: str = Field(default=None, description="라이선스 정보 페이지 URL")
    acquireLicensePage: str = Field(default=None, description="라이선스 획득 페이지 URL")