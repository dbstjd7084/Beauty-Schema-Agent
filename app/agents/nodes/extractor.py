from langchain_google_genai import ChatGoogleGenerativeAI
from ..state import GraphState
from app.schemas.product import ProductSchema
from app.core.llm import call_llm

# 1. LLM 및 구조화된 출력 설정
llm = call_llm()
structured_llm = llm.with_structured_output(ProductSchema)

def run(state: GraphState):
    print(f"--- Gemini 모델 추출 단계 (Simple Mode) ---")
    
    html_input = state.get('html_content', "")
    
    # 프롬프트를 스키마에 맞춰 간소화 (추가 필드 요청 제거)
    prompt = f"""당신은 HTML에서 상품명을 추출하는 전문가입니다.
    다음 HTML 소스에서 가장 핵심적인 '상품명' 하나만 찾아 JSON으로 반환하세요.
    
    HTML:
    {html_input}
    """
    
    try:
        # LLM 호출 -> ProductSchema 객체 반환
        result = structured_llm.invoke(prompt)
        
        # 결과를 딕셔너리로 변환 (alias 적용하여 @type 포함)
        extracted_dict = result.model_dump(by_alias=True)
        print("추출된 데이터:", extracted_dict)
        
        return {"extracted_data": extracted_dict}
    
    except Exception as e:
        print(f"추출 중 오류 발생: {e}")
        # GraphState의 errors 리스트에 에러 추가 (operator.add)
        return {"errors": [f"Extraction Error: {str(e)}"]}