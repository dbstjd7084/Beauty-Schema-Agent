from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from app.agents.graph import app as workflow

router = APIRouter()

class AnalysisRequest(BaseModel):
    url: str

# 테스트용 뷰티 상품 HTML 샘플
MOCK_BEAUTY_HTML = """
<div class="product-detail">
    <h1 class="p-name">[아모레] 헤라 블랙 쿠션 21호</h1>
    <div class="price-info">
        <span class="discount">20%</span>
        <span class="current-price">52,800원</span>
    </div>
    <div class="review-summary">
        <span class="rating">4.9</span>
        <span class="count">4,201개 리뷰</span>
    </div>
    <p class="description">강력한 커버력과 가벼운 밀착감을 동시에 선사하는 매트 쿠션의 정석</p>
</div>
"""

@router.post("/analyze")
async def start_analysis(request: AnalysisRequest):
    try:
        # 1. 실제 HTML 대신 테스트 데이터 사용 여부 결정
        if "test" in request.url.lower() or not request.url.startswith("http"):
            html_content = MOCK_BEAUTY_HTML
            print("--- 테스트 모드: Mock HTML을 사용합니다 ---")
        else:
            # 실제 URL인 경우에만 크롤링 실행
            async with httpx.AsyncClient() as client:
                response = await client.get(request.url, timeout=5.0)
                html_content = response.text

        # 2. 랭그래프 실행
        final_state = workflow.invoke({
            "url": request.url,
            "html_content": html_content,
            "retry_count": 0
        })

        # 3. 결과 반환
        return {
            "status": "success",
            "result": {
                "json_ld": final_state.get("extracted_data"),
                "logs": [
                    "System: 데이터 소스 준비 완료 (Mock/Real)",
                    f"Classifier: 선택된 스키마 -> {final_state.get('selected_schemas')}",
                    "Extractor: Gemini 모델이 가짜 HTML에서 정보를 추출했습니다."
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))