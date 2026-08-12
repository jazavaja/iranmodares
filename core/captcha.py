"""
Captcha handling for IranModares automation.
Includes screenshot capture, prediction, and form submission.
"""

import time
import os
from datetime import datetime
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import (
    SELECTORS,
    CAPTCHA_MAX_RETRIES,
    CAPTCHA_SCREENSHOT_TIMEOUT,
    CAPTCHA_ELEMENT_TIMEOUT,
    CAPTCHA_PAGE_LOAD_TIMEOUT,
    POST_SUBMIT_WAIT,
    VISIBILITY_CHECK_TIMEOUT,
    CAPTURES_DIR,
)

# Import ML predictor
from ml.predict_captcha import predict_captcha


class CaptchaSolver:
    """Handles captcha screenshot, prediction, and submission."""

    def __init__(self, page, logger):
        self.page = page
        self.logger = logger

    @staticmethod
    def _wait_visible(locator, timeout: int) -> bool:
        """Wait for locator to become visible. Returns True on success."""
        try:
            locator.first.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_captcha_form(self) -> bool:
        """
        Wait for full page load, then for img.item1 and input to appear.
        Same strategy as iran2.py / collect.py — patient wait for slow site.
        """
        print(f"⏳ Waiting for captcha page to fully load (up to {CAPTCHA_PAGE_LOAD_TIMEOUT // 1000}s)...")
        try:
            self.page.wait_for_load_state("load", timeout=CAPTCHA_PAGE_LOAD_TIMEOUT)
        except PlaywrightTimeoutError:
            print("⚠️ load event timed out, checking captcha element anyway...")

        captcha = self.page.locator(SELECTORS["captcha_image"])
        if not self._wait_visible(captcha, CAPTCHA_PAGE_LOAD_TIMEOUT):
            print("❌ Captcha image (img.item1) not found")
            return False

        captcha_input = self.page.locator(SELECTORS["captcha_input"])
        if not self._wait_visible(captcha_input, CAPTCHA_ELEMENT_TIMEOUT):
            print("❌ Captcha input not found")
            return False

        print("✅ Captcha page ready")
        return True

    def save_captcha(self, save_path: str) -> bool:
        """
        Capture captcha via page.screenshot + clip on img.item1 bounding box.
        Same method as iran2.py (commit 6f16ab0) — matches training data format.
        """
        try:
            captcha = self.page.locator(SELECTORS["captcha_image"])
            captcha.wait_for(state="visible", timeout=CAPTCHA_PAGE_LOAD_TIMEOUT)

            box = captcha.bounding_box(timeout=10000)
            if not box:
                raise Exception("Could not get captcha bounding box")

            self.page.screenshot(
                path=save_path,
                clip={
                    "x": box["x"],
                    "y": box["y"],
                    "width": box["width"],
                    "height": box["height"],
                },
                timeout=CAPTCHA_SCREENSHOT_TIMEOUT,
            )
            print(f"✅ Captcha screenshot saved: {save_path}")
            return True

        except Exception as e:
            print(f"❌ Captcha screenshot failed: {e}")
            return False

    def fill_and_submit(self, text: str) -> bool:
        """Fill captcha input and submit form."""
        captcha_input = self.page.locator(SELECTORS["captcha_input"])
        if not self._wait_visible(captcha_input, CAPTCHA_ELEMENT_TIMEOUT):
            print("❌ Captcha input not found")
            return False

        captcha_input.first.fill(text)
        print("✅ Captcha filled")

        submit_btn = self.page.locator(SELECTORS["captcha_submit"])
        if not self._wait_visible(submit_btn, CAPTCHA_ELEMENT_TIMEOUT):
            print("❌ Submit button not found")
            return False

        submit_btn.first.click()
        print("✅ Submit clicked")
        return True

    def check_solved(self) -> tuple[bool, str]:
        """
        Check if captcha was solved successfully.
        Returns: (is_solved, status) where status is 'success', 'fail', or 'ambiguous'
        """
        time.sleep(POST_SUBMIT_WAIT)

        captcha_form = self.page.locator(SELECTORS["captcha_form"])
        captcha_img = self.page.locator(SELECTORS["captcha_image"])

        form_visible = False
        img_visible = False

        try:
            form_visible = captcha_form.count() > 0 and captcha_form.first.is_visible(timeout=VISIBILITY_CHECK_TIMEOUT)
        except Exception:
            form_visible = False

        try:
            img_visible = captcha_img.count() > 0 and captcha_img.first.is_visible(timeout=VISIBILITY_CHECK_TIMEOUT)
        except Exception:
            img_visible = False

        if not form_visible and not img_visible:
            return True, "success"
        elif form_visible and img_visible:
            return False, "fail"
        else:
            return False, "ambiguous"

    def solve(self) -> bool:
        """
        Full captcha solving loop with retries.
        Returns True if solved, False if max retries exceeded.
        """
        if not self.wait_for_captcha_form():
            print("❌ Captcha form not ready, cannot solve")
            return False

        for attempt in range(1, CAPTCHA_MAX_RETRIES + 1):
            print(f"🔄 Captcha solve attempt {attempt}/{CAPTCHA_MAX_RETRIES}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            captcha_filename = f"captcha_{timestamp}.png"
            captcha_path = os.path.join(CAPTURES_DIR, captcha_filename)

            if not self.save_captcha(captcha_path):
                print("⚠️ Captcha screenshot failed, retrying...")
                time.sleep(2)
                continue

            text = predict_captcha(captcha_path)
            print(f"🔮 Predicted: {text}")

            if not self.fill_and_submit(text):
                print("⚠️ Form fill/submit failed, retrying...")
                self.logger.log(timestamp, captcha_filename, text, "submit_failed", attempt)
                time.sleep(2)
                continue

            solved, status = self.check_solved()

            if solved:
                print("✅ Captcha solved successfully! Form and captcha image disappeared.")
                self.logger.log(timestamp, captcha_filename, text, status, attempt)
                return True

            print(f"⚠️ Captcha {status}. Retrying...")
            self.logger.log(timestamp, captcha_filename, text, status, attempt)

        print("❌ Max retries reached. Captcha not solved.")
        return False
