import os
import shutil
import random


SOURCE_DIR = "../data/processed/chars"
DEST_DIR = "../data/dataset"


TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1


# ثابت بودن تقسیم
random.seed(42)



def create_folder(path):

    os.makedirs(
        path,
        exist_ok=True
    )



def split_dataset():


    # پاک کردن دیتاست قبلی (اختیاری)
    if os.path.exists(DEST_DIR):

        print("Removing old dataset...")

        shutil.rmtree(
            DEST_DIR
        )


    labels = sorted(
        os.listdir(SOURCE_DIR)
    )

    print("LABELS:", labels)


    total_train = 0
    total_val = 0
    total_test = 0



    for label in labels:


        source_folder = os.path.join(
            SOURCE_DIR,
            label
        )


        if not os.path.isdir(source_folder):
            continue



        images = [
            f for f in os.listdir(source_folder)
            if f.endswith(".png")
        ]


        # رندوم کردن
        random.shuffle(
            images
        )


        total = len(images)


        train_end = int(
            total * TRAIN_RATIO
        )


        val_end = int(
            total * (TRAIN_RATIO + VAL_RATIO)
        )


        train_files = images[:train_end]

        val_files = images[
            train_end:val_end
        ]

        test_files = images[
            val_end:
        ]



        splits = {

            "train": train_files,

            "val": val_files,

            "test": test_files

        }



        print(
            f"\n{label}: {total} images"
        )


        for split_name, files in splits.items():


            target_folder = os.path.join(
                DEST_DIR,
                split_name,
                label
            )


            create_folder(
                target_folder
            )


            for file in files:


                shutil.copy(

                    os.path.join(
                        source_folder,
                        file
                    ),

                    os.path.join(
                        target_folder,
                        file
                    )

                )


            print(
                f"  {split_name}: {len(files)}"
            )


            if split_name == "train":
                total_train += len(files)

            elif split_name == "val":
                total_val += len(files)

            else:
                total_test += len(files)



    print("\n====================")
    print("Dataset Created")
    print("====================")

    print(
        "Train:",
        total_train
    )

    print(
        "Validation:",
        total_val
    )

    print(
        "Test:",
        total_test
    )




if __name__ == "__main__":

    split_dataset()