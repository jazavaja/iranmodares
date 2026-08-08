import sys
import time
import pygame
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class Iranmodares:
    def __init__(self, profile_path):
        self.profile_path = profile_path
        self.playwright = None
        self.browser = None  # actually a BrowserContext (persistent)
        self.page = None
        self.init_browser()

    # ---------- utils ----------

    def wait_until_ready(self, time_count):
        for remaining in range(time_count, 0, -1):
            minutes = remaining // 60
            seconds = remaining % 60
            sys.stdout.write(f"\r  Remind: {minutes} : {seconds} ")
            sys.stdout.flush()
            time.sleep(1)
        print("\n Ohh okay countdown time done!")

    def bring_to_front(self):
        """
        Bring the tab to the front within the browser itself.
        Safe and simple - doesn't touch OS-level windows.
        """
        try:
            self.page.bring_to_front()
        except Exception as e:
            print(f"⚠️ Could not bring tab to front: {e}")

    def play_sound(self):
        pygame.mixer.init()
        sound = pygame.mixer.Sound("C:\\Windows\\Media\\Alarm02.wav")
        sound.play()
        pygame.time.delay(int(sound.get_length() * 1000))

    def safe_goto(self, url, retries=3, nav_timeout=15000):
        """
        Go to a URL without waiting for full page load.
        domcontentloaded fires as soon as the DOM is parsed and the
        elements we care about are usually interactable well before
        the 'load' event (images/fonts/ads finish loading).
        Retries only the navigation itself instead of restarting
        the whole browser.
        """
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=nav_timeout)
                return True
            except PlaywrightTimeoutError as e:
                last_err = e
                print(f"⚠️  goto timeout (attempt {attempt}/{retries}) for {url}")
                time.sleep(2)
        print(f"❌ goto failed after {retries} attempts: {last_err}")
        return False

    def wait_for_clickable(self, locator, timeout=15000):
        """
        Wait for a locator to actually be visible & enabled instead
        of relying on the page being 'fully' loaded.
        Returns True/False instead of raising, so caller can decide
        what to do next.
        """
        try:
            locator.first.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    # ---------- browser lifecycle ----------

    def init_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_path,
            headless=False,
            proxy=None,
            args=["--no-proxy-server"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36"
            ),
        )
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        # sane default navigation timeout for everything on this page
        self.page.set_default_navigation_timeout(15000)
        self.page.set_default_timeout(15000)

    def close(self):
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

    # ---------- actions ----------

    def doLogin(self):
        login_form = self.page.locator('form').filter(has_text="ورود به کنترل پنل")
        if not self.wait_for_clickable(login_form, timeout=15000):
            print("❌ Login form not found in time.")
            return False

        login_form.locator('input[name="email"]').fill("javadesmesh@gmail.com")
        login_form.locator('input[name="pass"]').fill("javad123@J")
        login_form.locator('input[type="submit"]').click()
        print("✅ Login Done!")
        return True

    def go_to_update(self):
        if not self.safe_goto('https://www.iranmodares.com/ControlPanel/advertisement.php?p=4'):
            return False

        print("Finding Link Update...")
        submit_button = self.page.locator('input[type="submit"].button')

        if self.wait_for_clickable(submit_button, timeout=10000):
            submit_button.first.click()
            print("✅ We clicked Go to Update, now you must resolve captcha.")
            self.bring_to_front()
            self.play_sound()
            return True
        else:
            print("The button was not found for updating, so we need to wait.")
            return False

    def run(self):
        while True:
            try:
                if not self.safe_goto('https://www.iranmodares.com/common-index.php?p=4'):
                    # navigation kept failing, short cooldown then retry the loop
                    time.sleep(5)
                    continue

                link = self.page.locator(
                    'a[href="https://www.iranmodares.com/ControlPanel/index.php"]'
                )

                if self.wait_for_clickable(link, timeout=8000):
                    print("✅ Link found, clicking")
                    link.first.click()
                else:
                    print("❌ Link not found, we must login")
                    if not self.doLogin():
                        time.sleep(5)
                        continue

                if not self.go_to_update():
                    time.sleep(5)
                    continue

                self.bring_to_front()
                input("⚠️ Enter the captcha and press Enter..")
                print("⏳ Waiting for the next Queue")
                self.wait_until_ready(1250)

            except Exception as e:
                print("❌ Error: ", e)
                self.close()
                self.init_browser()


if __name__ == '__main__':
    profile_path = r"C:\path\to\custom\profile"
    iranmodares = Iranmodares(profile_path)
    try:
        iranmodares.run()
    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted by user")
    finally:
        iranmodares.close()