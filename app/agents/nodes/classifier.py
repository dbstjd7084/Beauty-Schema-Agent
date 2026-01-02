from ..state import GraphState
from pydantic import BaseModel, Field
from typing import List, Literal
from app.core.llm import call_llm

SchemaType = Literal[
    "Product", "Organization", "Review", "Breadcrumb", 
    "Article", "ImageMeta", "LocalBusiness", "Video"
]

class ClassificationResult(BaseModel):
    selected_schemas: List[SchemaType] = Field(
        description="HTML 콘텐츠를 분석하여 추출이 필요한 스키마 리스트를 선택합니다."
    )
    reason: str = Field(description="이 스키마들을 선택한 이유에 대한 간략한 설명")

llm = call_llm()

classifier_llm = llm.with_structured_output(ClassificationResult)

def run(state: GraphState):
    print("--- LLM 기반 스키마 분류 단계 ---")
    
    html_input = state.get('html_content', "")
    
    prompt = f"""당신은 웹 페이지 구조 분석 전문가입니다. 
    제공된 HTML 소스를 분석하여, 아래 8가지 Schema.org 타입 중 추출 가능한 정보가 있는 타입을 모두 선택하세요.

    [선택 가능한 스키마 리스트]:
    1. Product: 제품명, 브랜드/제조사, 가격, 재고/판매 상태, 상세 설명 등 상품 자체 정보
    2. Organization: 브랜드/회사명, 로고, 공식 사이트, 고객센터 등 조직(기업) 기본 정보
    3. Review: 작성자, 평점, 작성일, 리뷰 본문 등 사용자 리뷰 및 평가 정보
    4. Breadcrumb: 현재 페이지의 위치를 나타내는 카테고리/경로(탐색 경로) 정보
    5. Article: 이벤트/공지/가이드/콘텐츠 글(본문, 작성자, 게시일 등) 정보
    6. ImageMeta: 상품/콘텐츠 이미지의 URL, 캡션(대체텍스트), 크기 등 이미지 메타데이터 정보
    7. LocalBusiness: 오프라인 매장/지점 정보(주소, 전화번호, 영업시간, 위치 등)
    8. Video: 영상 콘텐츠 정보(제목, 설명, 썸네일, 업로드일, 재생 URL 등)


    HTML 내용:
    {html_input[:3000]}
    """
    
    try:
        # LLM 호출
        result = classifier_llm.invoke(prompt)
        print(f"선택된 스키마: {result.selected_schemas} (이유: {result.reason})")
        
        return {
            "selected_schemas": result.selected_schemas,
            "retry_count": 0
        }
    except Exception as e:
        print(f"분류 중 오류 발생: {e}")
        return {"selected_schemas": ["Product"], "errors": [f"Classification Error: {str(e)}"]}