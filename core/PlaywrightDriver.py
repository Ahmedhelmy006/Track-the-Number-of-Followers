from playwright.async_api import async_playwright
import json

class PlaywrightDriver:
    def __init__(self, cookies_file=None):
        self.cookies_file = cookies_file

    async def initialize_driver(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()

            if self.cookies_file:
                with open(self.cookies_file, 'r') as file:
                    cookies = json.load(file)
                    await context.add_cookies(cookies)

            return context

    async def close(self, context):
        await context.close()
