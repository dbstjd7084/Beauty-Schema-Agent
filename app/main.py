import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# 이미지 구조에 맞춘 임포트 경로
from app.core.config import settings
from app.api.main import router as api_router  # app/api/main.py의 router를 가져옴

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Beauty Industry JSON-LD Generator AI Agent",
    version="1.0.0"
)

# 1. CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. API 라우터 등록 (app/api/main.py 연결)
app.include_router(api_router, prefix="/api", tags=["Analysis"])

# 3. 정적 파일 경로 설정 (image_6b4924.png 기준)
# app/static 폴더 위치를 잡습니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")

# 4. 서비스 메인 페이지 (Frontend) - 반드시 태그 포함
@app.get("/", tags=["Frontend"])
async def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))

# 5. 시스템 상태 체크 (System) - 반드시 태그 포함
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy", 
        "project": settings.PROJECT_NAME
    }