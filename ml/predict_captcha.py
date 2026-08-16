import cv2
import torch
import numpy as np

from .model import CharCNN


# =========================
# Settings
# =========================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "char_cnn.pth")

IMAGE_PATH = os.path.join(BASE_DIR, "..", "data", "raw", "images", "000001.png")

IMAGE_SIZE = 28


# =========================
# Device
# =========================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# =========================
# Load model
# =========================

model = CharCNN()

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device
    )
)

model = model.to(device)

model.eval()


# =========================
# Character classes
# =========================

classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

import cv2
import numpy as np


def crop_captcha_roi(img):
    """
    دریافت تصویر ورودی (۱۹۲x۷۲ یا هر ابعاد دیگر با پدینگ)
    و برش دقیق مستطیل سفید داخلی کپچا
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # پیدا کردن نواحی کاملاً روشن/سفید (بوم اصلی کپچا)
    # بوم داخلی پس‌زمینه سفید خالص/نزدیک به سفید دارد (> 240)
    _, white_mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # بزرگ‌ترین کانتور سفید، همان مستطیل کادر کپجاست
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        # اگر ابعاد استخراج شده معتبر بود، Crop می‌کنیم
        if w > 30 and h > 10:
            cropped = gray[y:y + h, x:x + w]
            # تغییر سایز دقیق به ابعاد ۱۰ task آموزش (100x20)
            resized = cv2.resize(cropped, (100, 20), interpolation=cv2.INTER_AREA)
            return resized

    # در صورت عدم کشف کانتور، ری‌سایز ساده fallback
    return cv2.resize(gray, (100, 20), interpolation=cv2.INTER_AREA)

# =========================
# Split characters
# =========================
def split_characters(image_path, debug=False, debug_dir=None):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # ذخیره تصویر اصلی
    if debug and debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(f"{debug_dir}/00_original.png", img)

    # =========================
    # روش جدید: مستقیماً resize به ۱۰۰x۲۰ (همون روش تست موفق)
    # =========================
    processed_img = cv2.resize(
        img,
        (100, 20),
        interpolation=cv2.INTER_AREA
    )

    # ذخیره بعد از resize
    if debug and debug_dir:
        cv2.imwrite(f"{debug_dir}/01_resized.png", processed_img)

    # =========================
    # آستانه‌گذاری
    # =========================
    _, thresh = cv2.threshold(
        processed_img,
        150,
        255,
        cv2.THRESH_BINARY_INV
    )

    # ذخیره بعد از threshold
    if debug and debug_dir:
        cv2.imwrite(f"{debug_dir}/02_threshold.png", thresh)

    # =========================
    # پیدا کردن کانتورها
    # =========================
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # فیلتر کردن نویزهای کوچک
        if h > 5 and w >= 2:
            boxes.append((x, y, w, h))

    # مرتب‌سازی باکس‌ها از چپ به راست
    boxes.sort(key=lambda box: box[0])

    # ذخیره تصویر با باکس‌ها
    if debug and debug_dir:
        debug_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        for x, y, w, h in boxes:
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.imwrite(f"{debug_dir}/03_boxes.png", debug_img)

        with open(f"{debug_dir}/04_info.txt", "w") as f:
            f.write(f"Number of boxes detected: {len(boxes)}\n")
            for i, (x, y, w, h) in enumerate(boxes):
                f.write(f"Box {i}: x={x}, y={y}, w={w}, h={h}\n")

    characters = []
    for i, (x, y, w, h) in enumerate(boxes):
        char = thresh[y:y + h, x:x + w]
        characters.append(char)

        if debug and debug_dir:
            cv2.imwrite(f"{debug_dir}/char_{i}.png", char)

    return characters

def resize_and_center(img, size=IMAGE_SIZE):

    h, w = img.shape

    scale = min(
        (size - 4) / w,
        (size - 4) / h
    )

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(
        img,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    canvas = np.zeros(
        (size, size),
        dtype=np.uint8
    )

    x = (size - new_w) // 2
    y = (size - new_h) // 2

    canvas[
        y:y + new_h,
        x:x + new_w
    ] = resized

    return canvas


def prepare_character(char):

    # تبدیل به uint8
    char = char.astype(
        np.uint8
    )

    char = resize_and_center(
        char,
        IMAGE_SIZE
    )


    # 0-255 → 0-1
    char = char.astype(
        np.float32
    ) / 255.0


    # H,W → 1,H,W
    char = np.expand_dims(
        char,
        axis=0
    )


    # 1,H,W → Tensor
    tensor = torch.tensor(
        char,
        dtype=torch.float32
    )


    # 1,H,W → 1,1,H,W
    tensor = tensor.unsqueeze(
        0
    )


    return tensor


# =========================
# Predict
# =========================

def predict_captcha(image_path):

    characters = split_characters(
        image_path
    )


    result = ""


    for char in characters:

        tensor = prepare_character(
            char
        )


        tensor = tensor.to(
            device
        )


        with torch.no_grad():

            output = model(
                tensor
            )


            prediction = torch.argmax(
                output,
                dim=1
            ).item()


        result += classes[
            prediction
        ]


    return result

def predict_single_character(image_path):

    img = cv2.imread(
        image_path,
        cv2.IMREAD_GRAYSCALE
    )

    if img is None:
        raise FileNotFoundError(image_path)

    img = cv2.resize(
        img,
        (28, 28),
        interpolation=cv2.INTER_AREA
    )

    img = img.astype(
        np.float32
    ) / 255.0

    img = np.expand_dims(
        img,
        axis=0
    )

    tensor = torch.tensor(
        img,
        dtype=torch.float32
    ).unsqueeze(0)

    tensor = tensor.to(device)

    with torch.no_grad():

        output = model(tensor)

        prediction = torch.argmax(
            output,
            dim=1
        ).item()

    return classes[prediction]