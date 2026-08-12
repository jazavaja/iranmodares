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

    def save_captcha(self, save_path: str) -> bool:
        """
        Capture captcha image using page.screenshot with clip.
        Avoids waiting for fonts by using bounding box.
        """
        try:
            captcha = self.page.locator(SELECTORS["captcha_image"])

            # Wait for element to be visible
            captcha.wait_for(state="visible", timeout=CAPTCHA_ELEMENT_TIMEOUT)

            # Get bounding box and capture with clip - no font waiting
            box = captcha.bounding_box(timeout=2000)
            if not box:
                raise Exception("Could not get captcha bounding box")

            self.page.screenshot(
                path=save_path,
                clip={
                    "x": box["x"],
                    "y": box["y"],
                    "width": box["width"],
                    "height": box["height"]
                },
                timeout=CAPTCHA_SCREENSHOT_TIMEOUT
            )
            print(f"✅ Captcha screenshot saved: {save_path}")
            return True

        except Exception as e:
            print(f"❌ Captcha screenshot failed: {e}")
            return False

    def fill_and_submit(self, text: str) -> bool:
        """Fill captcha input and submit form."""
        captcha_input = self.page.locator(SELECTORS["captcha_input"])
        if not captcha_input.first.wait_for(state="visible", timeout=CAPTCHA_ELEMENT_TIMEOUT):
            print("❌ Captcha input not found")
            return False

        captcha_input.first.fill(text)
        print("✅ Captcha filled")

        submit_btn = self.page.locator(SELECTORS["captcha_submit"])
        if not submit_btn.first.wait_for(state="visible", timeout=CAPTCHA_ELEMENT_TIMEOUT):
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
        except:
            form_visible = False

        try:
            img_visible = captcha_img.count() > 0 and captcha_img.first.is_visible(timeout=VISIBILITY_CHECK_TIMEOUT)
        except:
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
        for attempt in range(1, CAPTCHA_MAX_RETRIES + 1):
            print(f"🔄 Captcha solve attempt {attempt}/{CAPTCHA_MAX_RETRIES}")

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            captcha_filename = f"captcha_{timestamp}.png"
            captcha_path = os.path.join(CAPTURES_DIR, captcha_filename)

            # Capture captcha
            if not self.save_captcha(captcha_path):
                print(f"⚠️ Captcha screenshot failed, retrying...")
                time.sleep(1)
                continue

            # Predict
            text = predict_captcha(captcha_path)
            print(f"🔮 Predicted: {text}")

            # Fill and submit
            if not self.fill_and_submit(text):
                print("⚠️ Form fill/submit failed, retrying...")
                time.sleep(1)
                continue

            # Check result
            solved, status = self.check_solved()

            if solved:
                print("✅ Captcha solved successfully! Form and captcha image disappeared.")
                self.logger.log(timestamp, captcha_filename, text, status, attempt)
                return True
            else:
                print(f"⚠️ Captcha {status}: form_visible={not solved and status != 'ambiguous'}, img_visible={not solved}. Retrying...")
                self.logger.log(timestamp, captcha_filename, text, status, attempt)

        print("❌ Max retries reached. Captcha not solved.")
        return False