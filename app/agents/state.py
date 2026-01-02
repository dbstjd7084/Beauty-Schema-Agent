from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator

class ExtractionInput(TypedDict):
    schema_name: str     # 어떤 전문가가 실행될지 결정
    html_content: str    # 원본 데이터

class GraphState(TypedDict):
    url: str
    html_content: str
    media_map: Dict[str, Any]
    selected_schemas: List[str]
    schema_index: int
    extracted_data: Annotated[Dict[str, Any], operator.ior] 
    errors: Annotated[List[str], operator.add] 
    is_valid: bool
    retry_count: int