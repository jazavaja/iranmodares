import os
import csv
import tkinter as tk
from PIL import Image, ImageTk


IMAGE_DIR = "../data/raw/images"
LABEL_FILE = "../data/raw/labels.csv"


class LabelTool:

    def __init__(self, root):

        self.root = root
        self.root.title("Captcha Label Tool")

        self.labels = self.load_labels()

        self.images = sorted(
            [
                x for x in os.listdir(IMAGE_DIR)
                if x.endswith(".png")
                and "_threshold" not in x
            ]
        )

        self.index = 0


        # تصویر
        self.image_label = tk.Label(root)
        self.image_label.pack(
            padx=20,
            pady=20
        )


        # نمایش اسم فایل
        self.filename_label = tk.Label(
            root,
            font=("Arial", 12)
        )
        self.filename_label.pack()


        # ورودی
        self.entry = tk.Entry(
            root,
            font=("Arial", 18),
            justify="center"
        )

        self.entry.pack(
            pady=10
        )

        self.entry.bind(
            "<Return>",
            self.save_next
        )


        self.show_next()


    def load_labels(self):

        labels = {}

        if os.path.exists(LABEL_FILE):

            with open(
                LABEL_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                reader = csv.DictReader(f)

                for row in reader:
                    labels[row["filename"]] = row["label"]

        return labels



    def save_labels(self):

        with open(
            LABEL_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow(
                [
                    "filename",
                    "label"
                ]
            )

            for name, label in self.labels.items():

                writer.writerow(
                    [
                        name,
                        label
                    ]
                )



    def show_next(self):

        while self.index < len(self.images):

            filename = self.images[self.index]

            if filename not in self.labels:
                break

            self.index += 1


        if self.index >= len(self.images):

            self.filename_label.config(
                text="Finished 🎉"
            )

            return


        filename = self.images[self.index]

        path = os.path.join(
            IMAGE_DIR,
            filename
        )


        img = Image.open(path)


        # زوم 5 برابر
        img = img.resize(
            (
                img.width * 5,
                img.height * 5
            ),
            Image.Resampling.NEAREST
        )


        self.photo = ImageTk.PhotoImage(
            img
        )


        self.image_label.config(
            image=self.photo
        )


        self.filename_label.config(
            text=f"{self.index+1}/{len(self.images)}  {filename}"
        )


        self.entry.delete(
            0,
            tk.END
        )

        self.entry.focus()



    def save_next(self, event):

        text = self.entry.get().strip().upper()


        if len(text) != 5:

            self.filename_label.config(
                text="❌ باید 5 حرف باشد"
            )

            return


        filename = self.images[self.index]


        self.labels[filename] = text


        self.save_labels()


        self.index += 1

        self.show_next()



if __name__ == "__main__":

    root = tk.Tk()

    app = LabelTool(root)

    root.mainloop()