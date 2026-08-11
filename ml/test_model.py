import torch

from model import CharCNN
from dataset import create_dataloaders


# =========================
# Device
# =========================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# =========================
# Dataset
# =========================

_, _, test_loader = create_dataloaders(
    batch_size=32
)


# =========================
# Model
# =========================

model = CharCNN()

model.load_state_dict(
    torch.load(
        "char_cnn.pth",
        map_location=device
    )
)

model = model.to(device)

model.eval()


# =========================
# Test
# =========================

correct = 0
total = 0


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(device)
        labels = labels.to(device)


        outputs = model(images)


        predictions = outputs.argmax(
            dim=1
        )


        total += labels.size(0)

        correct += (
            predictions == labels
        ).sum().item()


accuracy = correct / total


print("======================")
print("Test Result")
print("======================")

print(
    f"Correct: {correct}/{total}"
)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)