from playwright.sync_api import sync_playwright
import os
import json

class PlaywrightDriver:
    def __init__(self, cookies_file=None, chrome_path="/usr/bin/google-chrome"):
        self.cookies_file = cookies_file
        self.chrome_path = chrome_path

    def initialize_driver(self):
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir="./chrome-profile",
            headless=False,
            executable_path=self.chrome_path 
        )

        if self.cookies_file and os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as file:
                cookies = json.load(file)
                context.add_cookies(cookies)

        return context

    def close(self, context):
        context.close()
