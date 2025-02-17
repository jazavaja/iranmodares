import time
import pygame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class Iranmodares:
    def __init__(self, profile_path):
        self.profile_path = profile_path
        self.driver = self.init_driver()

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={self.profile_path}")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36")
        return webdriver.Chrome(options=chrome_options)

    def doLogin(self):
        email_input = self.driver.find_element(By.NAME, "email")
        email_input.send_keys("javadesmesh@gmail.com")

        password_input = self.driver.find_element(By.NAME, "pass")
        password_input.send_keys("javad123@J")

        submit_button = self.driver.find_element(By.XPATH, '//input[@type="submit"]')
        submit_button.click()
        print("✅Login Done! ")

    def play_sound(self):
        pygame.mixer.init()
        sound = pygame.mixer.Sound("C:\\Windows\\Media\\Alarm02.wav")
        sound.play()
        pygame.time.delay(int(sound.get_length() * 1000))

    def go_to_update(self):
        self.driver.get('https://www.iranmodares.com/ControlPanel/advertisement.php?p=4')
        print("Finding Link Update... ")

        time.sleep(2)

        try:
            submit_button = self.driver.find_element(By.XPATH,
                                                     '//input[@type="submit" and @class="button"]')
            submit_button.click()
            print("✅ We clicked Go to Update now you must reslove captcha.")
            self.play_sound()
        except Exception as e:
            print(f"The button was not found for updating, so we need to wait.")

    def run(self):
        while True:
            try:
                self.driver.get('https://www.iranmodares.com/common-index.php?p=4')
                link = self.driver.find_elements(By.XPATH,
                                                 '//a[@href="https://www.iranmodares.com/ControlPanel/index.php"]')
                if link:
                    print("✅Link found, clicking")
                    link[0].click()
                else:
                    print("❌Link Not find we Must login")
                    self.doLogin()

                self.go_to_update()
                input("⚠️ Enter the captcha and press Enter..")
                print("⏳ Waiting for the next 30 minutes.")
                time.sleep(1300)

            except Exception as e:
                print("❌ Error: ", e)
                self.driver.quit()
                self.driver = self.init_driver()


if __name__ == '__main__':
    profile_path = r"C:\path\to\custom\profile"
    iranmodares = Iranmodares(profile_path)
    iranmodares.run()
