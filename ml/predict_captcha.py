import cv2
import torch
import numpy as np

from model import CharCNN


# =========================
# Settings
# =========================

MODEL_PATH = "char_cnn.pth"

IMAGE_PATH = "../data/raw/images/000001.png"

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


# =========================
# Split characters
# =========================

def split_characters(image_path):

    img = cv2.imread(
        image_path,
        cv2.IMREAD_GRAYSCALE
    )

    if img is None:
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )


    # Threshold
    _, thresh = cv2.threshold(
        img,
        150,
        255,
        cv2.THRESH_BINARY_INV
    )


    # Find contours
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    boxes = []


    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )


        # حذف نویز
        if h > 5 and w > 2:

            boxes.append(
                (x, y, w, h)
            )


    # چپ به راست
    boxes.sort(
        key=lambda box: box[0]
    )


    characters = []


    for x, y, w, h in boxes:

        char = thresh[
            y:y+h,
            x:x+w
        ]


        characters.append(
            char
        )


    return characters


# =========================
# Prepare character
# =========================

def prepare_character(char):

    # تبدیل به uint8
    char = char.astype(
        np.uint8
    )


    # تبدیل به PIL لازم نیست؛
    # مستقیماً با OpenCV resize می‌کنیم

    char = cv2.resize(
        char,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_AREA
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


    print(
        "Detected characters:",
        len(characters)
    )


    result = ""


    for i, char in enumerate(characters):

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


        letter = classes[
            prediction
        ]


        result += letter


        print(
            f"Character {i + 1}: {letter}"
        )


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



# =========================
# Main
# =========================

if __name__ == "__main__":
    result = predict_single_character(
        "../data/dataset/test/M/000159_1.png"
    )

    print("Prediction:", result)


    # =======================


    # result = predict_captcha(
    #     IMAGE_PATH
    # )
    #
    #
    # print()
    # print("======================")
    # print("CAPTCHA:", result)
    # print("======================")