from ..state import GraphState
from pydantic import BaseModel, Field
from typing import List, Literal
from app.core.llm import call_llm
from app.core.logger import crawler_logger, log_classification_result

SchemaType = Literal[
    "Product", "Organization", "Review", "Breadcrumb", 
    "Article", "ImageMeta", "LocalBusiness", "Video"
]

class SchemaTarget(BaseModel):
    schema_type: SchemaType = Field(description="추출할 스키마 타입")
    entity_name: str = Field(description="추출 대상의 이름이나 특징 (예: '메인 상품', '추천 상품', '고객 리뷰 섹션')")
    is_multiple: bool = Field(default=False, description="해당 타입의 데이터가 리스트 형태로 여러 개 존재하는지 여부")

class ClassificationResult(BaseModel):
    targets: List[SchemaTarget] = Field(
        description="HTML 콘텐츠에서 추출해야 할 대상 리스트"
    )
    reason: str = Field(description="이 대상들을 선택한 이유")

llm = call_llm()

classifier_llm = llm.with_structured_output(ClassificationResult)

def run(state: GraphState):
    ex_log = state.get("ex_log")
    if ex_log: ex_log.add("Classifier: 페이지 구조 분석 및 스키마 분류 시작...")

    crawler_logger.info("[Classifier] LLM 기반 스키마 분류 단계 진입")
    
    html_input = state.get('html_content', "")
    
    prompt = f"""당신은 웹 페이지 구조 분석 전문가입니다. 
    제공된 HTML 소스를 분석하여, 아래 8가지 Schema.org 타입 중 추출 가능한 정보가 있는 타입을 모두 선택하세요.

    [주의 사항]:
    1. 동일한 타입(예: Product)이 페이지 내에 여러 개 있다면, 한 타입으로 묶어 'is_multiple'을 true로 설정하세요.
    2. 하나의 정보가 여러 성격을 가진다면(예: 오프라인 매장이면서 미용실), 가장 구체적인 타입을 우선하되 관련 타입을 모두 고려하세요.
    3. 리스트 형태(예: 상품 목록, 리뷰 목록)로 존재하는 경우 'is_multiple'을 true로 설정하세요.
        
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
    {html_input}
    """
    
    try:
        print(f"[classifier] 스키마 분류 중... {prompt}")
        result = classifier_llm.invoke(prompt)
        extraction_tasks = [
            {"type": t.schema_type, "name": t.entity_name, "multiple": t.is_multiple} 
            for t in result.targets
        ]

        log_classification_result(result.targets, result.reason, ex_log=ex_log)
        
        return {
            "extraction_tasks": extraction_tasks,
            "retry_count": 0
        }
    except Exception as e:
        print(f"분류 중 오류 발생: {e}")
        return {"extraction_tasks": [{"type": "Product", "name": "Default", "multiple": True}], "errors": [str(e)]}