import asyncio
from playwright.async_api import async_playwright

async def fetch_url(target_url: str) -> str:
    """URL에 접속하여 렌더링된 HTML 소스를 반환합니다."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = await context.new_page()
        
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            
            for _ in range(3):
                await page.mouse.wheel(0, 1500)
                await page.wait_for_timeout(1500)
            
            return await page.content()
        finally:
            await browser.close()