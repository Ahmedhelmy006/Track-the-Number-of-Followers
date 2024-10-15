from playwright.sync_api import sync_playwright

class PlaywrightDriver:
    def __init__(self, profile_dir=None):
        self.profile_dir = profile_dir

    def initialize_driver(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch_persistent_context(
            self.profile_dir,
            headless=True
        )
        return browser

    def close(self, context):
        context.close()
