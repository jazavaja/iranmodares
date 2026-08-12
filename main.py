#!/usr/bin/env python3
"""
IranModares Advertisement Auto-Updater

Automates the process of updating advertisements on iranmodares.com
by handling login, navigation, captcha solving, and periodic updates.

Architecture:
- config.py: All constants and configuration
- core/browser.py: Browser lifecycle management
- core/navigation.py: Page navigation and interactions
- core/captcha.py: Captcha screenshot, prediction, submission
- core/logger.py: CSV logging for captcha attempts
- core/sound.py: Notification sounds
- ml/predict_captcha.py: ML model inference
"""

import sys
import time

from config import (
    BASE_DIR,
    NEXT_QUEUE_WAIT,
    ERROR_RECOVERY_WAIT,
)

from core import (
    BrowserManager,
    Navigator,
    CaptchaSolver,
    CaptchaLogger,
    play_alarm,
)


class IranModaresBot:
    """Main bot orchestrator."""

    def __init__(self, profile_path: str):
        self.browser = BrowserManager(profile_path)
        self.navigator = None
        self.captcha_solver = None
        self.logger = CaptchaLogger()

    def initialize(self):
        """Initialize all components."""
        self.browser.init_browser()
        self.navigator = Navigator(self.browser.page)
        self.captcha_solver = CaptchaSolver(self.browser.page, self.logger)

    def run(self):
        """Main automation loop."""
        print("🚀 IranModares Bot Started")
        print(f"📁 Captures directory: {BASE_DIR}/captures")
        self.logger.print_stats()

        while True:
            try:
                self._run_cycle()

            except KeyboardInterrupt:
                print("\n⚠️ Interrupted by user")
                break

            except Exception as e:
                print(f"❌ Unexpected error in main loop: {e}")
                print(f"🔄 Recovering in {ERROR_RECOVERY_WAIT}s...")
                time.sleep(ERROR_RECOVERY_WAIT)

        self.cleanup()

    def _run_cycle(self):
        """Single update cycle."""
        # 1. Go to common index
        if not self.navigator.go_to_common_index():
            time.sleep(5)
            return

        # 2. Click control panel link or login
        if not self.navigator.click_control_panel_link():
            print("❌ Link not found, we must login")
            if not self.navigator.do_login():
                time.sleep(5)
                return

        # 3. Wait for update button to be available
        if not self.navigator.wait_for_update_button():
            time.sleep(30)
            return

        # 4. Bring to front and play alarm
        self.browser.bring_to_front()
        play_alarm()

        # 5. Solve captcha
        if not self.captcha_solver.solve():
            print("❌ Captcha solving failed, returning to advertisement page")
            time.sleep(2)
            return

        # 6. Wait for next queue (20 minutes)
        print(f"⏳ Waiting for the next Queue ({NEXT_QUEUE_WAIT//60} min)")
        self.navigator.wait_until_ready(NEXT_QUEUE_WAIT)

    def cleanup(self):
        """Clean up resources."""
        print("🧹 Cleaning up...")
        self.browser.close()
        self.logger.print_stats()
        print("✅ Done")


def main():
    """Entry point."""
    if len(sys.argv) > 1:
        profile_path = sys.argv[1]
    else:
        profile_path = r"C:\path\to\custom\profile"
        print("⚠️  No profile path provided, using default")
        print("   Usage: python main.py <profile_path>")

    bot = IranModaresBot(profile_path)
    try:
        bot.initialize()
        bot.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        bot.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()