"""
Page navigation and interaction utilities for IranModares automation.
"""

import time
import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import (
    COMMON_INDEX_URL,
    CONTROL_PANEL_INDEX_URL,
    ADVERTISEMENT_URL,
    SELECTORS,
    DEFAULT_NAV_TIMEOUT,
    CAPTCHA_PAGE_LOAD_TIMEOUT,
)


class Navigator:
    """Handles page navigation and element interactions."""

    def __init__(self, page):
        self.page = page

    def safe_goto(self, url: str, retries: int = 3, nav_timeout: int = DEFAULT_NAV_TIMEOUT) -> bool:
        """
        Navigate to URL with fast commit strategy.
        Only waits for response headers, then elements are awaited separately.
        """
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                self.page.goto(url, wait_until="commit", timeout=nav_timeout)
                return True
            except PlaywrightTimeoutError as e:
                last_err = e
                print(f"⚠️  goto timeout (attempt {attempt}/{retries}) for {url}")
                time.sleep(2)
        print(f"❌ goto failed after {retries} attempts: {last_err}")
        return False

    def wait_for_clickable(self, locator, timeout: int = 15000) -> bool:
        """Wait for element to be visible and enabled."""
        try:
            locator.first.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def go_to_common_index(self) -> bool:
        """Navigate to common index page."""
        return self.safe_goto(COMMON_INDEX_URL)

    def click_control_panel_link(self) -> bool:
        """Click the control panel link if available."""
        link = self.page.locator(SELECTORS["control_panel_link"])
        if self.wait_for_clickable(link, timeout=8000):
            print("✅ Link found, clicking")
            link.first.click()
            return True
        return False

    def do_login(self) -> bool:
        """Perform login on control panel."""
        login_form = self.page.locator(SELECTORS["login_form"])
        if not self.wait_for_clickable(login_form, timeout=15000):
            print("❌ Login form not found in time.")
            return False

        from config import EMAIL, PASSWORD
        login_form.locator(SELECTORS["login_email"]).fill(EMAIL)
        login_form.locator(SELECTORS["login_password"]).fill(PASSWORD)
        login_form.locator(SELECTORS["login_submit"]).click()
        print("✅ Login Done!")
        return True

    def go_to_advertisement(self) -> bool:
        """Navigate to advertisement page."""
        return self.safe_goto(ADVERTISEMENT_URL, nav_timeout=30000)

    def click_update_button(self) -> bool:
        """Click the 'Go to Update' button."""
        print("Finding Link Update...")
        submit_button = self.page.locator(SELECTORS["update_submit_button"])

        if self.wait_for_clickable(submit_button, timeout=10000):
            submit_button.first.click()
            print("✅ We clicked Go to Update, waiting for captcha page...")
            try:
                self.page.wait_for_load_state("load", timeout=CAPTCHA_PAGE_LOAD_TIMEOUT)
                print("✅ Captcha page loaded.")
            except PlaywrightTimeoutError:
                print("⚠️ Page load slow — captcha solver will keep waiting.")
            return True
        else:
            print("The button was not found for updating, so we need to wait.")
            return False

    def go_to_update(self) -> bool:
        """Full flow: go to advertisement page and click update."""
        if not self.go_to_advertisement():
            return False
        return self.click_update_button()

    def get_wait_seconds_from_page(self):
        """
        Parse site's status text to calculate remaining wait time.
        Looks for: "هر X دقیقه" and "Y دقیقه پیش"
        """
        try:
            page_text = self.page.locator("body").inner_text()
        except Exception:
            return None

        interval_match = re.search(r'هر\s*(\d+)\s*دقیقه', page_text)
        elapsed_match = re.search(r'(\d+)\s*دقیقه\s*پیش', page_text)

        if not interval_match or not elapsed_match:
            return None

        interval_minutes = int(interval_match.group(1))
        elapsed_minutes = int(elapsed_match.group(1))
        remaining_minutes = interval_minutes - elapsed_minutes

        if remaining_minutes <= 0:
            return 0

        # Buffer for "19 دقیقه پیش" ambiguity + network delay
        buffer_seconds = 45
        return remaining_minutes * 60 + buffer_seconds

    def wait_for_update_button(self, poll_interval: int = 60, max_wait: int = 1500) -> bool:
        """
        Wait for update button to become available.
        Uses site's own countdown text when available.
        """
        from config import POLL_INTERVAL, MAX_WAIT_FOR_UPDATE

        elapsed = 0
        while elapsed <= max_wait:
            if self.go_to_update():
                return True

            smart_wait = self.get_wait_seconds_from_page()
            if smart_wait is not None:
                minutes, seconds = divmod(smart_wait, 60)
                print(f"⏳ Site says update unlocks in ~{minutes}m {seconds}s. Waiting exactly that long.")
                self.wait_until_ready(smart_wait)
                elapsed += smart_wait
            else:
                print(f"⏳ Couldn't read exact remaining time from page, rechecking in {poll_interval}s")
                time.sleep(poll_interval)
                elapsed += poll_interval

        print("❌ Update button never became available within max_wait, giving up this cycle.")
        return False

    @staticmethod
    def wait_until_ready(time_count: int):
        """Display countdown timer."""
        import sys
        for remaining in range(time_count, 0, -1):
            minutes = remaining // 60
            seconds = remaining % 60
            sys.stdout.write(f"\r  Remind: {minutes} : {seconds} ")
            sys.stdout.flush()
            time.sleep(1)
        print("\n Ohh okay countdown time done!")