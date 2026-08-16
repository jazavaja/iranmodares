# برای تست با دیباگ
from ml.predict_captcha import split_characters

characters = split_characters(
    "captures/captcha_20260816_220358_909.png",  # بدون ../ چون از پوشه modares اجرا می‌شه
    debug=True,
    debug_dir="ml/debug"  # دیباگ توی پوشه ml ذخیره بشه
)

print(f"تعداد کاراکترهای تشخیص داده شده: {len(characters)}")