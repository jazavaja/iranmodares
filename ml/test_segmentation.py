import cv2
import os


IMAGE_PATH = "../captures/captcha_20260816_220358_909.png"
DEBUG_DIR = "../debug"

os.makedirs(DEBUG_DIR, exist_ok=True)


img = cv2.imread(IMAGE_PATH)


# 1 - تصویر اصلی بزرگ شده فقط برای دید
big = cv2.resize(
    img,
    None,
    fx=5,
    fy=5,
    interpolation=cv2.INTER_NEAREST
)

cv2.imwrite(
    f"{DEBUG_DIR}/0_original_big.png",
    big
)


# 2 - خاکستری
gray = cv2.cvtColor(
    img,
    cv2.COLOR_BGR2GRAY
)

cv2.imwrite(
    f"{DEBUG_DIR}/1_gray.png",
    gray
)


# 3 - threshold
_, thresh = cv2.threshold(
    gray,
    150,
    255,
    cv2.THRESH_BINARY_INV
)

cv2.imwrite(
    f"{DEBUG_DIR}/2_threshold.png",
    thresh
)
# ========================================================

img = cv2.imread(
    f"{DEBUG_DIR}/2_threshold.png",
    cv2.IMREAD_GRAYSCALE
)


# پیدا کردن قسمت‌های سفید
contours, _ = cv2.findContours(
    img,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)


boxes = []


for c in contours:

    x, y, w, h = cv2.boundingRect(c)

    boxes.append(
        (x,y,w,h)
    )


# چپ به راست
boxes.sort(
    key=lambda x:x[0]
)


print(len(boxes))


for i, (x,y,w,h) in enumerate(boxes):

    char = img[
        y:y+h,
        x:x+w
    ]

    cv2.imwrite(
        f"char_{i}.png",
        char
    )




