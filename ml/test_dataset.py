from dataset import create_dataloaders


train_loader, val_loader, test_loader = create_dataloaders(
    batch_size=32
)


images, labels = next(iter(train_loader))


print("Images shape:", images.shape)
print("Labels shape:", labels.shape)

print("First labels:")
print(labels[:10])