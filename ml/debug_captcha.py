import os
import cv2
import torch
import numpy as np

from model import CharCNN

MODEL_PATH = "char_cnn.pth"
IMAGE_PATH = "../data/raw/images/000001.png"
IMAGE_SIZE = 28

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = CharCNN()
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model = model.to(device)
model.eval()

classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

os.makedirs("debug", exist_ok=True)


def resize_and_center(img, size=28):
    h, w = img.shape
    scale = min((size - 4) / w, (size - 4) / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((size, size), dtype=np.uint8)
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas[y:y + new_h, x:x + new_w] = resized
    return canvas


img = cv2.imread(IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

boxes = []
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    if h > 5 and w > 2:
        boxes.append((x, y, w, h))
boxes.sort(key=lambda b: b[0])

print("Ground truth: HTPES")
print("Detected characters:", len(boxes))

for i, (x, y, w, h) in enumerate(boxes):
    char = thresh[y:y + h, x:x + w]
    cv2.imwrite(f"debug/char_{i}_original.png", char)
    print(f"char {i}: bbox=({x},{y},{w},{h}) shape={char.shape}")

    stretched = cv2.resize(char, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"debug/char_{i}_stretched_28.png", stretched)

    centered = resize_and_center(char)
    cv2.imwrite(f"debug/char_{i}_centered_28.png", centered)

    for name, arr in [("STRETCHED (current predict_captcha)", stretched),
                      ("CENTERED  (training-style)   ", centered)]:
        t = arr.astype(np.float32) / 255.0
        t = torch.tensor(t, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)
        with torch.no_grad():
            out = model(t)
            pred = torch.argmax(out, dim=1).item()
        print(f"  {name}: -> {classes[pred]}")
