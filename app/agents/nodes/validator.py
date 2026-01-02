from ..state import GraphState
from pydantic import BaseModel, Field
from app.core.llm import call_llm
from typing import List

class ValidationResult(BaseModel):
    is_valid: bool = Field(description="모든 데이터가 비즈니스 로직에 적합하고 누락이 없으면 True")
    reason: str = Field(description="검증 결과에 대한 요약 설명")
    missing_fields: List[str] = Field(default=[], description="누락되었거나 보완이 필요한 필드 목록")


llm = call_llm()

validator_llm = llm.with_structured_output(ValidationResult)

def run(state: GraphState):
    print("--- LLM 기반 검증 단계 ---")
    
    extracted_data = state.get("extracted_data", {})
    selected_schemas = state.get("selected_schemas", [])

    if not extracted_data:
        return {"is_valid": False, "errors": ["추출된 데이터가 전혀 없습니다."]}

    prompt = f"""당신은 데이터 품질 검증 전문가입니다. 
    다음 HTML 소스와 추출된 JSON 데이터를 비교하여 데이터의 정확성과 완전성을 검증하세요.

    [검증 대상 스키마]: {selected_schemas}
    [추출된 데이터]: {extracted_data}
    
    [검증 규칙]:
    1. 선택된 각 스키마에 해당하는 정보가 올바른 구조로 작성되었는가?
    2. 필수 필드가 모두 포함되었는가?
    """

    try:
        response = validator_llm.invoke(prompt)
        
        return {
            "is_valid": response.is_valid,
            "errors": [f"[{f}] 필드 누락/오류: {response.reason}" for f in response.missing_fields] if not response.is_valid else []
        }
    except Exception as e:
        return {"errors": [f"Validation Error: {str(e)}"]}