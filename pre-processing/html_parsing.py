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
    
    # [추가] 중복 제거를 위한 Set (이미지 URL의 경로 기준)
    seen_img_urls = set()
    # [추가] 필터링할 플레이스홀더 키워드
    placeholders = ['750.png', 'defaultImages', 'blank.gif', 'loading.gif']

    # 2. 모든 태그 순회
    for tag in list(soup.find_all(True)):
        if not tag or not hasattr(tag, 'attrs'):
            continue
            
        # --- [미디어 식별 섹션] ---
        if tag.name == 'img':
            # [해결 1] Lazy Loading 대응: data-src를 src보다 우선해서 가져옴
            img_url = tag.get('data-src') or tag.get('src')
            
            # [해결 2] Placeholder 필터링: 유효하지 않은 이미지는 스킵
            if not img_url or any(p in img_url for p in placeholders):
                tag.decompose()
                continue
            
            # [해결 3] 중복 제거: 쿼리 스트링(?...)을 제외한 순수 URL로 비교
            base_url = img_url.split('?')[0]
            if base_url in seen_img_urls:
                tag.decompose()
                continue
            
            seen_img_urls.add(base_url)
            
            alt_text = tag.get('alt', '설명 없음').strip()
            # 텍스트 내에 이미지를 삽입하는 마크다운 형식 유지
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

        # 나머지 속성 정제 로직
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
    print(f"✅ 분석 완료: 이미지 {img_count}개(중복/필터 제외), 동영상 {vid_count}개 감지됨")
    
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
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            for i in range(3):
                await page.mouse.wheel(0, 1500)
                await page.wait_for_timeout(1500) # 로딩 대기

            content = await page.content()
            final_md, img_c, vid_c = refined_semantic_processor(content)
            
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
    URL = "https://www.amoremall.com/kr/ko/store/gate?srsltid=AfmBOooPQQmPZ2Ky_nz7qhF_GOp4aag5oM7w3jrBwyP-rHgyCwe7TOiH"
    
    result_json = asyncio.run(run_crawler(URL))

    if result_json:
        file_name = "amore_refined_output.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(result_json, f, ensure_ascii=False, indent=4)
        print(f"\n📂 정제된 JSON 파일 저장 완료: {file_name}")
    else:
        print("\n⚠️ 저장할 결과물이 없습니다.")