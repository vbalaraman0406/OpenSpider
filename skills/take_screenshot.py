import asyncio
from playwright.async_api import async_playwright

async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 1800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        url = 'https://www.amazon.com/s?k=high+pressure+shower+head+with+jet+mode+multiple+settings'
        print('Navigating to Amazon...')
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # Wait for search results to load
        await page.wait_for_timeout(5000)
        
        # Scroll down slightly to get past any top banners
        await page.evaluate('window.scrollBy(0, 250)')
        await page.wait_for_timeout(2000)
        
        # Take screenshot
        screenshot_path = '/Users/vbalaraman/OpenSpider/amazon_shower_heads.png'
        await page.screenshot(path=screenshot_path, full_page=False)
        
        print(f'Screenshot saved to {screenshot_path}')
        
        # Also check if we got results
        result_count = await page.evaluate('document.querySelectorAll("[data-component-type=s-search-result]").length')
        print(f'Found {result_count} search results on page')
        
        await browser.close()

asyncio.run(take_screenshot())
