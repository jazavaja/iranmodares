import sys
import time
import pygame
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, ProxySettings


class Iranmodares:
    def __init__(self, profile_path):
        self.profile_path = profile_path
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.init_browser()

    def wait_until_ready(self, time_count):
        countdown_time = time_count

        for remaining in range(countdown_time, 0, -1):
            minutes = remaining // 60
            seconds = remaining % 60
            sys.stdout.write(f"\r  Remind: {minutes} : {seconds} ")
            sys.stdout.flush()
            time.sleep(1)

        print("\n Ohh okay countdown time done!")

    def init_browser(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_path,
            headless=False,
            proxy=None,
            args=["--no-proxy-server"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36"
        )


        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()

        self.page.goto("https://api.ipify.org")
        print("IP shown in browser:", self.page.content())
        time.sleep(1)
    def doLogin(self):
        login_form = self.page.locator('form').filter(has_text="ورود به کنترل پنل")

        login_form.locator('input[name="email"]').fill("javadesmesh@gmail.com")
        login_form.locator('input[name="pass"]').fill("javad123@J")
        login_form.locator('input[type="submit"]').click()
        print("✅Login Done! ")

    def play_sound(self):
        pygame.mixer.init()
        sound = pygame.mixer.Sound("C:\\Windows\\Media\\Alarm02.wav")
        sound.play()
        pygame.time.delay(int(sound.get_length() * 1000))

    def go_to_update(self):
        self.page.goto('https://www.iranmodares.com/ControlPanel/advertisement.php?p=4')
        print("Finding Link Update... ")

        time.sleep(2)

        try:
            submit_button = self.page.locator('input[type="submit"].button')
            submit_button.click(timeout=5000)
            print("✅ We clicked Go to Update now you must resolve captcha.")
            self.play_sound()
        except PlaywrightTimeoutError:
            print(f"The button was not found for updating, so we need to wait.")

    def run(self):
        while True:
            try:
                self.page.goto('https://www.iranmodares.com/common-index.php?p=4', timeout=60000)

                link = self.page.locator('a[href="https://www.iranmodares.com/ControlPanel/index.php"]')

                if link.count() > 0:
                    print("✅Link found, clicking")
                    link.first.click()
                else:
                    print("❌Link Not find we Must login")
                    self.doLogin()

                self.go_to_update()
                input("⚠️ Enter the captcha and press Enter..")
                print("⏳ Waiting for the next Queue")
                self.wait_until_ready(1250)

            except Exception as e:
                print("❌ Error: ", e)
                self.close()
                self.init_browser()

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


if __name__ == '__main__':
    profile_path = r"C:\path\to\custom\profile"
    iranmodares = Iranmodares(profile_path)
    try:
        iranmodares.run()
    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted by user")
    finally:
        iranmodares.close()