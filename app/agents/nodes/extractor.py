from ..state import GraphState
from app.schemas.registry import SCHEMA_MAP
from app.core.llm import call_llm
from app.core.processor import resolve_media_links 
llm = call_llm()

def run(state: GraphState):
    idx = state.get("schema_index", 0)
    schemas = state.get("selected_schemas", [])
    media_map = state.get("media_map", {})
    
    if idx >= len(schemas):
        return {}

    target_schema_name = schemas[idx]
    schema_class = SCHEMA_MAP.get(target_schema_name)
    
    print(f"--- [{idx+1}/{len(schemas)}] {target_schema_name} 전문가 추출 단계 ---")
    
    structured_llm = llm.with_structured_output(schema_class)
    html_input = state.get('html_content', "")
    
    prompt = f"당신은 {target_schema_name} 정보 추출 전문가입니다. HTML에서 해당 정보를 JSON으로 추출하세요."
    
    try:
        result = structured_llm.invoke(prompt + f"\nHTML: {html_input}")
        data_dict = result.model_dump(by_alias=True)
        
        # --- [핵심: 특정 스키마일 경우 즉시 URL 치환] ---
        if target_schema_name in ["Video", "ImageMeta"]:
            # 추출된 딕셔너리 내부의 [IMG_XXX], [VID_XXX]를 실제 URL로 바꿈
            data_dict = resolve_media_links(data_dict, media_map)
            print(f"🔗 {target_schema_name} 미디어 링크 치환 완료")

        return {
            "extracted_data": {target_schema_name: data_dict},
            "schema_index": idx + 1
        }
    except Exception as e:
        print(f"❌ {target_schema_name} 추출 에러: {e}")
        return {"errors": [str(e)], "schema_index": idx + 1}