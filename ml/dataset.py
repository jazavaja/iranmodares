from torchvision import datasets, transforms
from torch.utils.data import DataLoader


DATASET_DIR = "../data/dataset"


# تبدیل تصویر به Tensor
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor()
])


def create_dataloaders(batch_size=32):

    train_dataset = datasets.ImageFolder(
        f"{DATASET_DIR}/train",
        transform=transform
    )

    val_dataset = datasets.ImageFolder(
        f"{DATASET_DIR}/val",
        transform=transform
    )

    test_dataset = datasets.ImageFolder(
        f"{DATASET_DIR}/test",
        transform=transform
    )


    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )


    return (
        train_loader,
        val_loader,
        test_loader
    )