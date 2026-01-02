import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.main import router as api_router
from app.agents.graph import app as workflow

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Beauty Industry JSON-LD Generator AI Agent",
    version="1.0.0",
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["Analysis"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", tags=["Frontend"])
async def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy", 
        "project": settings.PROJECT_NAME
    }

# uvicorn app.main:app --reload