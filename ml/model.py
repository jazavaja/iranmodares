import torch.nn as nn


class CharCNN(nn.Module):

    def __init__(self):

        super().__init__()


        self.network = nn.Sequential(

            # 28x28x1
            nn.Conv2d(
                1,
                32,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2),
            # 14x14x32



            nn.Conv2d(
                32,
                64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.MaxPool2d(2),
            # 7x7x64



            nn.Flatten(),


            nn.Linear(
                64 * 7 * 7,
                128
            ),

            nn.ReLU(),


            nn.Linear(
                128,
                26
            )

        )


    def forward(self, x):

        return self.network(x)