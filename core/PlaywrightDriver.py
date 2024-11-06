from playwright.sync_api import sync_playwright
import os

class PlaywrightDriver:
    def __init__(self, chrome_path="/usr/bin/google-chrome"):
        # Path to the extracted profile directory
        self.user_data_dir = "./chrome-profile"
        self.chrome_path = chrome_path

    def initialize_driver(self):
        playwright = sync_playwright().start()

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,  
            headless=False,                   
            executable_path=self.chrome_path   
        )

        print("Chrome launched with persistent profile data.")

        return context

    def close(self, context):
        # Close the browser context, which saves any updates to the profile
        context.close()
        print("Chrome context closed and session saved.")
