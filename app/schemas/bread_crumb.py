from .base import BaseSchema
from pydantic import Field
from typing import List

# target_schema_name = current_task["type"]
# entity_name = current_task["name"]

prompt = """
당신은 **target_schema_name SEO 구조화 데이터 전문가**입니다.
대상은 **entity_name**이며, 이를 기반으로 마크업을 생성하세요.

[지침]:
1. [출력 예시]와 같이 주소에 포함된 언어 설정(/kr/ko)의 경우 트레일의 시작에 포함하지 않는 최상위 주소로 취급합니다.
2. 해당 대상과 관련된 유효한 정보만 `application/ld+json` 스크립트 형식으로 추출하세요.

[필수 속성]:
- itemListElement: 각 트레일 항목을 `ListItem` 유형의 배열로 포함하세요. 각 항목에는 다음 속성이 포함되어야 합니다:
    ListItem 속성:
    - position: 트레일 내 항목의 순서를 나타내는 정수입니다
    - name: 항목의 표시 이름입니다
    - item: 해당 경로의 URL입니다

[출력 예시]:
{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Books",
    "item": "https://example.com/books"
    },{
    "@type": "ListItem",
    "position": 2,
    "name": "Science Fiction",
    "item": "https://example.com/books/sciencefiction"
    },{
    "@type": "ListItem",
    "position": 3,
    "name": "Award Winners"
    }]
},
{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Literature",
    "item": "https://example.com/kr/ko/literature"
    },{
    "@type": "ListItem",
    "position": 2,
    "name": "Award Winners"
    }]
}
"""

class ListItem(BaseSchema):
    type: str = Field(default="ListItem", alias="@type")
    position: int
    name: str
    item: str = Field(..., description="해당 경로의 URL")

class BreadCrumbSchema(BaseSchema):
    type: str = Field(default="BreadcrumbList", alias="@type")
    itemListElement: List[ListItem]