from .base import BaseSchema
from pydantic import Field
from typing import List

# target_schema_name = current_task["type"]
# entity_name = current_task["name"]

prompt = """
당신은 **target_schema_name SEO 구조화 데이터 전문가**입니다.
대상은 **entity_name**이며, 이를 기반으로 마크업을 생성하세요.

[지침]:
1. 필수 속성은 없으며, 구글이 페이지를 더 잘 이해할 수 있도록 권장 속성을 최대한 포함하세요.
2. 해당 대상과 관련된 유효한 정보만 `application/ld+json` 스크립트 형식으로 추출하세요.

[권장 속성]:
- @type: 대상을 기반으로 `Article`, `NewsArticle`, `BlogPosting` 중 가장 적합한 유형 하나를 선택합니다.
- image: 기사를 나타내거나 관련된 이미지를 [IMG_XXX] 형태로 작성하세요.
- author: '작성자 마크업 권장사항'에 따라 `Person` 또는 `Organization` 유형으로 작성하세요.
    - author.name: 작성자의 전체 이름을 정확히 기재하세요.
    - author.url: 작성자의 소셜미디어, 내 정보, 약력 페이지와 같은 고유 식별 웹페이지 URL을 기재하세요.
- datePublished & dateModified: 기사가 게시된 시간과 최근 수정된 시간을 ISO 8601 형식으로 정확히 기재하세요.
- headline: [제목 작성 권장사항]에 따른 핵심 제목을 작성합니다.

[제목 작성 권장사항]:
- 구체적이고 간결한 텍스트: '제품 배송 지연 안내'와 같이 사이트를 나타내는 구체적인 제목을 작성하세요. 일반적인 제목(예: '홈페이지', '제품')은 피하세요.
- 유인 키워드 반복 금지: 검색결과를 스팸으로 오인할 수 있습니다.
- 반복되는 텍스트 또는 상용구 텍스트 금지: 각 페이지마다 콘텐츠를 설명하는 ‘고유한’ 텍스트가 있어야 한다. 또한, ‘밴드 이름 - 동영상, 가사’처럼 제목에 필요 없는 내용을 포함하지 말아야 합니다.
- 제목 브랜드화: ‘ExampleSocialSite| 가입하고 새로운 계정을 사용하세요.’ 처럼 시작 또는 끝에 사이트 이름을 넣고, 막대(|) 구분자로 나머지 텍스트와 분리합니다.
- 동일한 언어와 문자 체계: 페이지를 한국어로 작성했다면 제목도 한국어로 작성합니다. 예외 문자 체계인 알파벳은 언어와 문자 체계와 상관 없이 포함될 수 있습니다.
- 가격 정보 포함 금지: 가격이 변동으로 실제 가격과 일치하지 않을 수 있습니다.

[작성자 마크업 권장사항]:
- author과 publisher의 name은 필수 속성입니다
- 여러 명의 작성자를 지정할 경우 각 작성자를 하나의 author 필드에 나열합니다
- 저자를 더 잘 이해할 수 있도록 @type과 url 속성을 사용하는 것이 좋습니다
- author에는 Person 또는 Organization만이 @type에 들어갈 수 있습니다
- publisher에는 Organization만이 @type에 들어갈 수 있습니다

[출력 예시]:
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "Breaking News| Major Event Unfolds in City",
  "image": [
    "https://example.com/photos/1x1/photo.jpg",
    "https://example.com/photos/4x3/photo.jpg",
    "https://example.com/photos/16x9/photo.jpg"
    ],
  "datePublished": "2024-01-05T08:00:00+08:00",
  "dateModified": "2024-02-05T09:20:00+08:00",
  "author": [{
      "@type": "Person",
      "name": "Jane Doe",
      "url": "https://example.com/profile/janedoe123"
    },{
      "@type": "Person",
      "name": "John Doe",
      "url": "https://example.com/profile/johndoe123"
  }]
  "publisher":[
    {
      "@type": "Organization",
      "name": "The Daily Bug",
      "url": "https://www.example.com"
  }]
}
"""

class ArticleSchema(BaseSchema):
    type: str = Field(default="Article", alias="@type")
    headline: str = Field(default=None, description="기사 제목")
    image: List[str] = Field(default=None, description="대표 이미지 목록")
    dateModified: str = Field(default=None, description="수정일 (ISO 8601 형식)")
    datePublished: str = Field(default=None, description="발행일 (ISO 8601 형식)")
    author: dict = Field(default=None, description="작성자 정보 (type: Person/Organization)")