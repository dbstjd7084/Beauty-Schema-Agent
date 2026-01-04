from ..state import GraphState
from app.schemas.registry import SCHEMA_MAP
from app.core.llm import call_llm
from app.core.processor import resolve_media_links 
from app.core.logger import extractor_logger, log_extraction_result

llm = call_llm()

def run(state: GraphState):
    idx = state.get("schema_index", 0)
    tasks = state.get("extraction_tasks", [])
    media_map = state.get("media_map", {})
    ex_log = state.get("ex_log")
    
    if idx >= len(tasks):
        return {}

    current_task = tasks[idx]
    target_schema_name = current_task["type"]    # 예: "Product"
    entity_name = current_task["name"]           # 예: "설화수 자음생크림 (메인)"
    is_multiple = current_task.get("multiple", False)

    schema_class = SCHEMA_MAP.get(target_schema_name)
    
    extractor_logger.info(f"분석 시작: {target_schema_name} ({entity_name})")

    structured_llm = llm.with_structured_output(schema_class)
    html_input = state.get('html_content', "")
    
    prompt = f"""당신은 {target_schema_name} 정보 추출 전문가입니다. 
                지금 당신이 추출해야 할 구체적인 대상은 **"{entity_name}"** 입니다. 

                [지침]:
                - 해당 대상과 관련된 정보만 정확히 JSON으로 추출하세요.
                - 이미지 경로는 반드시 [IMG_XXX] 형태로 출력합니다.
                """
    
    if is_multiple:
        prompt += f"\n- 페이지 내에 해당 타입의 데이터가 여러 개 존재하므로, 리스트(Array) 형태로 모두 추출하세요."
    
    try:
        result = structured_llm.invoke(prompt + f"\nHTML: {html_input}")
        data_dict = result.model_dump(by_alias=True)
        log_extraction_result(target_schema_name, data_dict, ex_log=ex_log)

        data_dict = resolve_media_links(data_dict, media_map)
        print(f"[Extractor] {target_schema_name} 미디어 링크 치환 완료")

        return {
            "extracted_data": {f"{target_schema_name}": data_dict},
            "schema_index": idx + 1
        }
    except Exception as e:
        print(f"❌ {target_schema_name} 추출 에러: {e}")
        return {"errors": [str(e)], "schema_index": idx + 1}