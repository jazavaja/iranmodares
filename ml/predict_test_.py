from ml.predict_captcha import predict_captcha
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_IMAGE = os.path.join(
        BASE_DIR,
        "..",
        "captures",
        "captcha_20260813_121814_437.png"
    )


result = predict_captcha(TEST_IMAGE)

print("Prediction:", result)