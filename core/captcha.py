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
        استخراج پیکسل‌های تصویر جاری از حافظه DOM مرورگر بدون ارسال درخواست مجدد به سرور
        """
        try:
            captcha = self.page.locator(SELECTORS["captcha_image"])
            captcha.wait_for(state="visible", timeout=CAPTCHA_PAGE_LOAD_TIMEOUT)

            # خواندن بایت‌های تصویر مستقیم از حافظه مرورگر با Canvas
            base64_data = captcha.evaluate("""
                (img) => {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth || 100;
                    canvas.height = img.naturalHeight || 20;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    return canvas.toDataURL('image/png').split(',')[1];
                }
            """)

            import base64
            image_bytes = base64.b64decode(base64_data)
            with open(save_path, "wb") as f:
                f.write(image_bytes)

            print(f"✅ Captcha raw image extracted from DOM: {save_path}")
            return True

        except Exception as e:
            print(f"❌ Captcha DOM extraction failed: {e}")
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

        Success:
            .form-confirm containing the success message is visible.

        Fail:
            Success message is not found.
        """

        time.sleep(POST_SUBMIT_WAIT)

        success_message = self.page.locator(
            "div.form-confirm"
        )

        try:
            if success_message.count() > 0 and success_message.first.is_visible(
                    timeout=VISIBILITY_CHECK_TIMEOUT
            ):
                text = success_message.first.inner_text().strip()

                print(f"✅ Success message found: {text}")

                return True, "success"

        except Exception:
            pass

        print("❌ Success message not found")

        return False, "fail"

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
