import csv
import cv2
import os


INPUT_DIR = "../data/raw/images"
OUTPUT_DIR = "../data/processed/chars"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


def split_characters(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return []


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


    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    boxes = []


    for c in contours:

        x, y, w, h = cv2.boundingRect(c)

        if h > 5 and w > 2:

            boxes.append(
                (x,y,w,h)
            )


    boxes.sort(
        key=lambda box: box[0]
    )


    chars = []


    for x,y,w,h in boxes:

        char = thresh[
            y:y+h,
            x:x+w
        ]

        chars.append(char)


    return chars



def save_char(char_img, label, filename, index):

    folder = os.path.join(
        OUTPUT_DIR,
        label
    )

    os.makedirs(
        folder,
        exist_ok=True
    )


    save_path = os.path.join(
        folder,
        f"{filename}_{index}.png"
    )

    char_img = resize_and_center(
        char_img
    )

    cv2.imwrite(
        save_path,
        char_img
    )

import cv2
import numpy as np


def resize_and_center(img, size=28):

    h, w = img.shape


    # اندازه حداکثر مجاز
    scale = min(
        (size-4) / w,
        (size-4) / h
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


    # وسط چین
    x = (size - new_w) // 2
    y = (size - new_h) // 2


    canvas[
        y:y+new_h,
        x:x+new_w
    ] = resized


    return canvas

if __name__ == "__main__":


    csv_path = "../data/raw/labels.csv"


    with open(
        csv_path,
        "r",
        encoding="utf-8"
    ) as f:


        reader = csv.DictReader(f)


        success = 0
        failed = 0


        for row in reader:


            filename = row["filename"]
            label = row["label"]


            image_path = os.path.join(
                INPUT_DIR,
                filename
            )


            chars = split_characters(
                image_path
            )


            # باید 5 حرف باشد
            if len(chars) != len(label):

                print(
                    "❌ Wrong:",
                    filename,
                    "found:",
                    len(chars),
                    "expected:",
                    len(label)
                )

                failed += 1
                continue



            for i, char_img in enumerate(chars):
                print(f"CharImage: {char_img} - Label: {label[i]}")
                save_char(
                    char_img,
                    label[i],
                    filename.replace(".png",""),
                    i
                )


            success += 1


            # print(
            #     f"✅ {filename} done"
            # )


    print("================")
    print(
        "Success:",
        success
    )

    print(
        "Failed:",
        failed
    )