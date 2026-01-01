from typing import TypedDict, List, Dict, Any, Annotated
import operator

class GraphState(TypedDict):
    # 입력 데이터
    url: str
    html_content: str
    
    # 처리 과정 데이터
    selected_schemas: List[str]  # 분류기가 선택한 스키마
    extracted_data: Dict[str, Any] # 추출된 JSON 결과
    
    # 품질 관리
    errors: Annotated[List[str], operator.add] # 에러 메시지 누적
    retry_count: int