import torch
import torch.nn as nn
import torch.optim as optim

from model import CharCNN
from dataset import create_dataloaders


# =========================
# تنظیمات
# =========================

EPOCHS = 30
BATCH_SIZE = 32
LEARNING_RATE = 0.001

MODEL_PATH = "char_cnn.pth"


# =========================
# Device
# =========================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)


# =========================
# Data
# =========================

train_loader, val_loader, test_loader = create_dataloaders(
    batch_size=BATCH_SIZE
)


print(
    "Train samples:",
    len(train_loader.dataset)
)

print(
    "Validation samples:",
    len(val_loader.dataset)
)

print(
    "Test samples:",
    len(test_loader.dataset)
)


# =========================
# Model
# =========================

model = CharCNN()

model = model.to(device)


# =========================
# Loss
# =========================

criterion = nn.CrossEntropyLoss()


# =========================
# Optimizer
# =========================

optimizer = optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# =========================
# Training
# =========================

best_val_accuracy = 0.0


for epoch in range(EPOCHS):

    # ---------------------
    # TRAIN
    # ---------------------

    model.train()

    train_loss = 0.0
    train_correct = 0
    train_total = 0


    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)


        # صفر کردن gradient
        optimizer.zero_grad()


        # Forward
        outputs = model(images)


        # محاسبه loss
        loss = criterion(
            outputs,
            labels
        )


        # Backpropagation
        loss.backward()


        # آپدیت وزن‌ها
        optimizer.step()


        # statistics
        train_loss += loss.item()

        _, predicted = torch.max(
            outputs,
            1
        )


        train_total += labels.size(0)

        train_correct += (
            predicted == labels
        ).sum().item()


    train_accuracy = (
        train_correct / train_total
    )


    train_loss = (
        train_loss / len(train_loader)
    )


    # ---------------------
    # VALIDATION
    # ---------------------

    model.eval()

    val_loss = 0.0
    val_correct = 0
    val_total = 0


    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)


            outputs = model(images)


            loss = criterion(
                outputs,
                labels
            )


            val_loss += loss.item()


            _, predicted = torch.max(
                outputs,
                1
            )


            val_total += labels.size(0)

            val_correct += (
                predicted == labels
            ).sum().item()


    val_accuracy = (
        val_correct / val_total
    )


    val_loss = (
        val_loss / len(val_loader)
    )


    # ---------------------
    # PRINT
    # ---------------------

    print(
        f"Epoch [{epoch + 1}/{EPOCHS}] "
        f""
        f"Train Loss: {train_loss:.4f} "
        f"Train Acc: {train_accuracy * 100:.2f}% "
        f""
        f"Val Loss: {val_loss:.4f} "
        f"Val Acc: {val_accuracy * 100:.2f}%"
    )


    # ---------------------
    # SAVE BEST MODEL
    # ---------------------

    if val_accuracy > best_val_accuracy:

        best_val_accuracy = val_accuracy

        torch.save(
            model.state_dict(),
            MODEL_PATH
        )

        print(
            f"  ✓ Best model saved "
            f"({best_val_accuracy * 100:.2f}%)"
        )


print("\n======================")
print("Training finished")
print("======================")

print(
    f"Best validation accuracy: "
    f"{best_val_accuracy * 100:.2f}%"
)

print(
    f"Model saved to: {MODEL_PATH}"
)