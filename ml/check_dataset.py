import os
from collections import Counter


DATASET_DIR = "../data/processed/chars"


counter = Counter()

print("__ ",os.listdir(DATASET_DIR))
for letter in os.listdir(DATASET_DIR):

    folder = os.path.join(
        DATASET_DIR,
        letter
    )

    if os.path.isdir(folder):

        count = len([
            f for f in os.listdir(folder)
            if f.endswith(".png")
        ])

        counter[letter] = count



print("===================")
print("Dataset Statistics")
print("===================")


total = 0

for letter, count in sorted(counter.items()):

    print(
        f"{letter}: {count}"
    )

    total += count


print("===================")
print(
    "Total chars:",
    total
)