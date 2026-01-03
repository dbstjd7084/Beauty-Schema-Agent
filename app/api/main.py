from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.graph import app as workflow
from app.core.loader import fetch_url
from app.core.processor import preprocess_pipeline
from app.core.logger import ExecutionLogger
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

@router.post("/analyze")
async def start_analysis(request: AnalysisRequest):
    ex_log = ExecutionLogger()
    ex_log.add(f"분석 시작: {request.url}")

    if "test" in request.url.lower() or not request.url.startswith("http"):
        html_content = MOCK_BEAUTY_HTML 
        media_map = {"images": {}, "videos": {}}
    else:
        ex_log.add("URL 접속 및 HTML 수집 중...")
        raw_html = await fetch_url(request.url) 
        ex_log.add(f"수집 완료 ({len(raw_html)} bytes)")
        ex_log.add("마크다운 전처리 중...")
        html_content, media_map = preprocess_pipeline(raw_html)
        ex_log.add(f"미디어 추출 완료: IMG({len(media_map['images'])})")
    
    ex_log.add("AI 에이전트 분석 실행...")
    final_state = workflow.invoke({
        "url": request.url,
        "html_content": html_content, # 정제된 마크다운 텍스트
        "media_map": media_map,  
        "ex_log": ex_log,  
        "schema_index": 0,            
        "retry_count": 0
    })

    return {
        "status": "success",
        "result": {
            "json_ld": final_state.get("extracted_data"),
            "media_used": media_map,
            "is_live": final_state.get("is_live", False),
            "logs": ex_log.get_logs()
        }
    }