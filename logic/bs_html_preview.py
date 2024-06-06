import asyncio
from playwright.async_api import async_playwright

async def get_preview():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(java_script_enabled=True)
        await page.set_viewport_size({'width': 1000, 'height':820})
        await page.goto('file:/Users/baypso/Documents/fisht/source/bs_maps/map.html')
        await page.wait_for_timeout(500)
        await page.screenshot(path='source/screen.png')
        await page.close()
        await browser.close()

asyncio.run(get_preview())