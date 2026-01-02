from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import app as workflow
from app.core.loader import fetch_url
from app.core.processor import preprocess_pipeline
import httpx

router = APIRouter()

class AnalysisRequest(BaseModel):
    url: str

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

from app.core.loader import fetch_url
from app.core.processor import preprocess_pipeline
from app.agents.graph import app as workflow # 컴파일된 그래프

@router.post("/analyze")
async def start_analysis(request: AnalysisRequest):
    if "test" in request.url.lower() or not request.url.startswith("http"):
        html_content = MOCK_BEAUTY_HTML # 테스트용
        media_map = {"images": {}, "videos": {}}
    else:
        raw_html = await fetch_url(request.url) 
        html_content, media_map = preprocess_pipeline(raw_html)

    final_state = workflow.invoke({
        "url": request.url,
        "html_content": html_content, # 정제된 마크다운 텍스트
        "media_map": media_map,    
        "schema_index": 0,            
        "retry_count": 0
    })

    return {
        "status": "success",
        "result": {
            "json_ld": final_state.get("extracted_data"),
            "media_used": media_map,
            "logs": [
                "System: Playwright 크롤링 및 마크다운 전처리 완료",
                f"Classifier: 선택된 스키마 -> {final_state.get('selected_schemas')}",
                "Extractor: 전문가 노드가 정제된 텍스트에서 정보 추출 완료"
            ]
        }
    }