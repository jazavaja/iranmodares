"""
Configuration constants for IranModares automation.
"""

import os

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
CAPTCHA_LOG_CSV = os.path.join(CAPTURES_DIR, "captcha_log.csv")

# URLs
BASE_URL = "https://www.iranmodares.com"
COMMON_INDEX_URL = f"{BASE_URL}/common-index.php?p=4"
CONTROL_PANEL_INDEX_URL = f"{BASE_URL}/ControlPanel/index.php"
ADVERTISEMENT_URL = f"{BASE_URL}/ControlPanel/advertisement.php?p=4"

# Credentials (should be moved to env vars in production)
EMAIL = "javadesmesh@gmail.com"
PASSWORD = "javad123@J"

# Browser settings
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36"
)
HEADLESS = False
DEFAULT_NAV_TIMEOUT = 30000
DEFAULT_ELEMENT_TIMEOUT = 15000

# Timing
CAPTCHA_MAX_RETRIES = 2
CAPTCHA_PAGE_LOAD_TIMEOUT = 120000  # wait up to 2 min for slow site load
CAPTCHA_SCREENSHOT_TIMEOUT = 30000
CAPTCHA_ELEMENT_TIMEOUT = 15000
POST_SUBMIT_WAIT = 2
VISIBILITY_CHECK_TIMEOUT = 1000
MAX_WAIT_FOR_UPDATE = 1500
POLL_INTERVAL = 60
NEXT_QUEUE_WAIT = 1250  # ~20 minutes
ERROR_RECOVERY_WAIT = 3
LOGIN_RETRY_WAIT = 5
NAV_RETRY_WAIT = 5

# Sound
ALARM_SOUND = r"C:\Windows\Media\Alarm02.wav"

# Selectors
SELECTORS = {
    "login_form": 'form:has-text("ورود به کنترل پنل")',
    "login_email": 'input[name="email"]',
    "login_password": 'input[name="pass"]',
    "login_submit": 'input[type="submit"]',
    "control_panel_link": 'a[href="https://www.iranmodares.com/ControlPanel/index.php"]',
    "update_submit_button": 'input[type="submit"].button',
    "captcha_image": "img.item1",
    "captcha_input": 'input[name="imagecode"]',
    "captcha_submit": 'input[type="submit"].button',
    "captcha_form": 'form[name="f"]',
}

# Captcha model
MODEL_PATH = os.path.join(BASE_DIR, "ml", "char_cnn.pth")
IMAGE_SIZE = 28
CLASSES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")