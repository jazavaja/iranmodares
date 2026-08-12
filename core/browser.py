"""
Browser lifecycle management for IranModares automation.
"""

import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from config import (
    USER_AGENT,
    HEADLESS,
    DEFAULT_NAV_TIMEOUT,
    DEFAULT_ELEMENT_TIMEOUT,
)


class BrowserManager:
    """Manages Playwright browser lifecycle."""

    def __init__(self, profile_path: str):
        self.profile_path = profile_path
        self.playwright = None
        self.browser = None  # persistent context
        self.page = None

    def init_browser(self):
        """Initialize persistent browser context."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_path,
            headless=HEADLESS,
            proxy=None,
            args=["--no-proxy-server"],
            user_agent=USER_AGENT,
        )
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        self.page.set_default_navigation_timeout(DEFAULT_NAV_TIMEOUT)
        self.page.set_default_timeout(DEFAULT_ELEMENT_TIMEOUT)

    def close(self):
        """Clean up browser resources."""
        if self.browser:
            try:
                self.browser.close()
            except Exception as e:
                print(f"ℹ️ Browser was already closed: {e}")
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                print(f"ℹ️ Playwright already stopped: {e}")
        self.browser = None
        self.playwright = None
        self.page = None

    def restart(self):
        """Restart browser session."""
        self.close()
        time.sleep(1)
        self.init_browser()

    def bring_to_front(self):
        """Bring current tab to front."""
        try:
            self.page.bring_to_front()
        except Exception as e:
            print(f"⚠️ Could not bring tab to front: {e}")