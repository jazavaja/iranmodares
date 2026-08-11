from playwright.sync_api import sync_playwright
import cv2
import os
import time


SAVE_DIR = "../data/raw/images"


def preprocess_image(image_path):

    img = cv2.imread(image_path)

    img = cv2.resize(
        img,
        None,
        fx=5,
        fy=5,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    _, thresh = cv2.threshold(
        gray,
        150,
        255,
        cv2.THRESH_BINARY_INV
    )

    output = image_path.replace(
        ".png",
        "_threshold.png"
    )

    cv2.imwrite(
        output,
        thresh
    )

    return output

def download_captcha(index):

    os.makedirs(
        SAVE_DIR,
        exist_ok=True
    )

    filename = f"{index:06d}.png"

    path = os.path.join(
        SAVE_DIR,
        filename
    )


    # جلوگیری از cache
    url = (
        "https://www.iranmodares.com/"
        "security-image.php?"
        f"{time.time()}"
    )


    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(url)

        img = page.locator("img")

        img.wait_for()


        img.screenshot(
            path=path
        )


        browser.close()


    print(
        "Saved:",
        path
    )


    preprocess_image(path)

def get_next_index():

    os.makedirs(
        SAVE_DIR,
        exist_ok=True
    )

    files = [
        f for f in os.listdir(SAVE_DIR)
        if f.endswith(".png")
        and "_threshold" not in f
    ]

    if not files:
        return 1

    numbers = [
        int(f.replace(".png", ""))
        for f in files
    ]

    return max(numbers) + 1

if __name__ == "__main__":

    start = get_next_index()

    total = 10

    for i in range(start, start + total):

        download_captcha(i)

        print(
            f"{i} done"
        )