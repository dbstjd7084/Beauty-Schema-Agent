from app.core.loader import fetch_url
from app.core.processor import preprocess_pipeline

async def main(url: str):
    # 1. 로딩 (Crawling)
    raw_html = await fetch_url(url)
    
    # 2. 전처리 (Processing & Media Key Replacement)
    # 이 과정에서 이미지/영상은 [IMG_001]로 바뀌고 별도의 dict에 저장됨
    final_text, media_info = preprocess_pipeline(raw_html)
    
    # 3. 결과 구성
    result = {
        "content": final_text,
        "media_map": media_info # {'images': {'IMG_001': {...}}, 'videos': {...}}
    }
    return result