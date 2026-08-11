from playwright.sync_api import sync_playwright
import pytesseract
import cv2


# مسیر Tesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


URL = "https://www.iranmodares.com/security-image.php?1786392526"


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(URL)

    img = page.locator("img")

    img.wait_for()

    img.screenshot(
        path="captcha.png"
    )

    print("✅ Image saved")

    browser.close()



# ---------- OCR ----------

import cv2


img = cv2.imread("captcha.png")


# بزرگ کردن برای دید بهتر
img = cv2.resize(
    img,
    None,
    fx=5,
    fy=5,
    interpolation=cv2.INTER_CUBIC
)


# خاکستری
gray = cv2.cvtColor(
    img,
    cv2.COLOR_BGR2GRAY
)


# تبدیل به سیاه و سفید
_, thresh = cv2.threshold(
    gray,
    150,
    255,
    cv2.THRESH_BINARY_INV
)


cv2.imwrite(
    "threshold.png",
    thresh
)


# پیدا کردن کانتور ها
contours, _ = cv2.findContours(
    thresh,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)


chars = []


for contour in contours:

    x, y, w, h = cv2.boundingRect(contour)

    # حذف نویزهای کوچک
    if w * h > 20:

        char = thresh[
            y:y+h,
            x:x+w
        ]

        chars.append(
            (x, char)
        )


# مرتب سازی از چپ به راست
chars = sorted(
    chars,
    key=lambda c: c[0]
)


print("Characters:", len(chars))


# ذخیره حروف جدا شده
for index, (x, char) in enumerate(chars):

    cv2.imwrite(
        f"char_{index}.png",
        char
    )

    print(
        "saved:",
        f"char_{index}.png"
    )