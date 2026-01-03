import re
import json
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def replace_media_with_keys(soup: BeautifulSoup):
    """이미지 및 동영상을 [IMG_001] 형태의 키로 치환하고 맵을 반환합니다."""
    media_map = {"images": {}, "videos": {}}
    img_idx, vid_idx = 1, 1
    seen_urls = set()

    for tag in soup.find_all(['img', 'video', 'iframe']):
        if tag.name == 'img':

            url = tag.get('data-src') or tag.get('src') or "unknown"
            alt = tag.get('alt', 'no-description').strip()
            
            base_url = url.split('?')[0]
            if base_url in seen_urls:
                tag.decompose()
                continue
            
            seen_urls.add(base_url)
            
            img_id = f"IMG_{img_idx:03d}"
            media_map["images"][img_id] = {"url": url, "alt": alt}
            tag.replace_with(f" [{img_id} | {alt}] ")
            img_idx += 1
            
        elif tag.name == 'video' or (tag.name == 'iframe' and 'youtube' in (tag.get('src') or '')):
            vid_id = f"VID_{vid_idx:03d}"
            url = tag.get('src') or "unknown"
            
            if url in seen_urls:
                tag.decompose()
                continue
            seen_urls.add(url)

            media_map["videos"][vid_id] = {"url": url}
            tag.replace_with(f" [{vid_id}] ")
            vid_idx += 1
            
    return soup, media_map

def clean_html_tags(soup: BeautifulSoup):
    """불필요한 태그 및 속성을 제거합니다."""
    unwanted = ['script', 'style', 'header', 'footer', 'nav', 'aside', 'noscript', 'svg', 'meta']
    for tag in soup(unwanted):
        tag.decompose()
    return soup

def finalize_text(text: str) -> str:
    """최종 텍스트의 공백 및 특수문자를 정규화합니다."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\|[^\]]*]', ']', text)
    return text.strip()

def preprocess_pipeline(html_content: str):
    """모든 전처리 과정을 순차적으로 실행합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    soup = clean_html_tags(soup)
    soup, media_map = replace_media_with_keys(soup)
    markdown_text = md(str(soup), heading_style="atx")
    cleaned_text = finalize_text(markdown_text)
    
    return cleaned_text, media_map

def resolve_media_links(data, media_map):
    """추출된 JSON 데이터 내의 [IMG_XXX] 키를 실제 URL로 치환합니다."""
    json_str = json.dumps(data, ensure_ascii=False)
    
    for img_id, info in media_map.get('images', {}).items():
        # [IMG_001] 문자열을 실제 URL로 교체
        json_str = json_str.replace(img_id, info['url'])
        
    for vid_id, info in media_map.get('videos', {}).items():
        json_str = json_str.replace(vid_id, info['url'])
        
    return json.loads(json_str)