import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def refined_semantic_processor(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 제거할 태그 (디자인/스크립트 노이즈)
    unwanted_tags = ['script', 'style', 'header', 'footer', 'nav', 'aside', 'noscript', 'meta', 'svg']
    for tag in soup(unwanted_tags):
        tag.decompose()

    img_count = 0
    vid_count = 0

    # 2. 모든 태그 순회
    for tag in list(soup.find_all(True)):
        if not tag or not hasattr(tag, 'attrs'):
            continue
            
        # --- [미디어 식별 섹션] ---
        if tag.name == 'img':
            img_url = tag.get('src') or tag.get('data-src') or "URL 없음"
            alt_text = tag.get('alt', '설명 없음').strip()
            tag.insert_before(f"\n\n[🖼️ 이미지 발견 | 설명: {alt_text} | 경로: {img_url}]\n\n")
            img_count += 1
            tag.decompose()
            continue
        
        elif tag.name == 'video':
            video_url = tag.get('src')
            if not video_url:
                source_tag = tag.find('source')
                video_url = source_tag.get('src') if source_tag else "URL 없음"
            tag.insert_before(f"\n\n[🎥 동영상 발견 | 경로: {video_url}]\n\n")
            vid_count += 1
            tag.decompose()
            continue

        elif tag.name == 'iframe' and 'youtube' in (tag.get('src') or ''):
            yt_url = tag.get('src')
            tag.insert_before(f"\n\n[📺 외부 동영상(YouTube) | 경로: {yt_url}]\n\n")
            vid_count += 1
            tag.decompose()
            continue

        # --- [속성 필터링 및 가시화 섹션] ---
        new_attrs = {}
        current_attrs = tag.attrs if tag.attrs is not None else {}
        
        for attr, value in current_attrs.items():
            if attr == 'aria-label' or 'area' in attr or 'name' in attr:
                simplified_key = attr.replace('ap-click-', '')
                new_attrs[simplified_key] = value

        tag.attrs = new_attrs

        if new_attrs:
            attr_string = " | ".join([f"{k}: {v}" for k, v in new_attrs.items()])
            if tag.get_text(strip=True):
                tag.insert_before(f" {{#{attr_string}}} ")

    markdown_text = md(str(soup), heading_style="atx")
    print(f"✅ 분석 완료: 이미지 {img_count}개, 동영상 {vid_count}개 감지됨")
    
    # 미디어 개수 정보도 함께 반환하기 위해 튜플 형태로 리턴
    return markdown_text.strip(), img_count, vid_count

async def run_crawler(target_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"🌐 접속 중: {target_url}")
        
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(7000) 
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(2000)

            content = await page.content()
            final_md, img_c, vid_c = refined_semantic_processor(content)
            
            # JSON에 담을 데이터 구조 생성
            result_data = {
                "target_url": target_url,
                "crawl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "media_stats": {
                    "image_count": img_c,
                    "video_count": vid_c
                },
                "info": final_md
            }
            
            return result_data

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return None
        finally:
            await browser.close()

if __name__ == "__main__":
    URL = "https://www.amoremall.com/kr/ko/aibc/web/"
    
    # 1. 크롤링 실행 및 결과 받기 (딕셔너리 형태)
    result_json = asyncio.run(run_crawler(URL))

    # 2. 결과가 있으면 JSON 파일로 저장
    if result_json:
        file_name = "amore_live_output.json"
        
        # 저장 폴더가 없다면 생성 (선택 사항)
        # os.makedirs("output", exist_ok=True)
        # file_path = os.path.join("output", file_name)

        with open(file_name, "w", encoding="utf-8") as f:
            # indent=4로 보기 좋게 포맷팅, ensure_ascii=False로 한글 보존
            json.dump(result_json, f, ensure_ascii=False, indent=4)
        
        print(f"\n📂 JSON 파일 저장 완료: {file_name}")
    else:
        print("\n⚠️ 저장할 결과물이 없습니다.")