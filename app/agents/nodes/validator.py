from ..state import GraphState
from pydantic import BaseModel, Field
from app.core.llm import call_llm
from typing import List
from app.core.logger import crawler_logger, log_validation_result, log_final_output

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="모든 데이터가 비즈니스 로직에 적합하고 누락이 없으면 True")
    is_live: bool = Field(default=False, description="현재 페이지에서 실시간 라이브 방송(Live Streaming)이 진행 중인지 여부")
    reason: str = Field(description="검증 결과에 대한 요약 설명")
    missing_fields: List[str] = Field(default=[], description="누락되었거나 보완이 필요한 필드 목록")

llm = call_llm()
validator_llm = llm.with_structured_output(ValidationResult)

def run(state: GraphState):
    crawler_logger.info("[Validator] 데이터 품질 및 실시간 상태 검증 진입")
    
    extracted_data = state.get("extracted_data", {})
    tasks = state.get("extraction_tasks", [])

    if not extracted_data:
        crawler_logger.warning("[Validator] 추출된 데이터가 없어 검증을 중단합니다.")
        return {"is_valid": False, "is_live": False, "errors": ["추출된 데이터가 전혀 없습니다."]}

    prompt = f"""당신은 데이터 품질 검증 전문가입니다. 
    다음 HTML 소스와 추출된 JSON 데이터를 비교하여 데이터의 정확성과 완전성을 검증하세요.

    [검증 대상 스키마]: {tasks}
    [추출된 데이터]: {extracted_data}
    
    [검증 규칙]:
    1. 선택된 각 스키마에 해당하는 정보가 올바른 구조로 작성되었는가?
    2. 필수 필드가 모두 포함되었는가?
    3. 만약 라이브 방송이 감지된다면 'is_live'를 True로 설정하세요.
    """

    try:
        response = validator_llm.invoke(prompt)
        crawler_logger.info("[Validator] 데이터 품질 검증 완료")

        log_validation_result(
            is_valid=response.is_valid, 
            reason=response.reason, 
            missing_fields=response.missing_fields
        )

        if response.is_valid:
            log_final_output(extracted_data)
        
        return {
            "is_valid": response.is_valid,
            "is_live": response.is_live,
            "errors": [f"[{f}] 필드 누락/오류: {response.reason}" for f in response.missing_fields] if not response.is_valid else []
        }
    except Exception as e:
        crawler_logger.error(f"[Validator] 검증 도중 에러 발생: {str(e)}")
        return {"errors": [f"Validation Error: {str(e)}"]}