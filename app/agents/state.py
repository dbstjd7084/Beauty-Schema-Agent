from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator

class ExtractionInput(TypedDict):
    schema_name: str 
    html_content: str 

class GraphState(TypedDict):
    url: str
    html_content: str
    media_map: Dict[str, Any]
    extraction_tasks: List[dict]
    schema_index: int
    extracted_data: Annotated[Dict[str, Any], operator.ior] 
    errors: Annotated[List[str], operator.add] 
    is_valid: bool
    is_live: bool 
    ex_log: Any
    retry_count: int