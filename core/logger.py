"""
CSV logging for captcha attempts.
"""

import os
import csv
from datetime import datetime

from config import CAPTCHA_LOG_CSV


class CaptchaLogger:
    """Logs captcha attempts to CSV for analysis."""

    def __init__(self, csv_path: str = CAPTCHA_LOG_CSV):
        self.csv_path = csv_path
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Create CSV with header if it doesn't exist."""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # بدون header - فقط داده
                # writer.writerow(["timestamp", "filename", "prediction", "result", "attempt"])
                pass

    def log(self, timestamp: str, filename: str, prediction: str, result: str, attempt: int):
        """Log a single captcha attempt."""
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, filename, prediction, result, attempt])

    def get_stats(self) -> dict:
        """Get statistics from log file."""
        if not os.path.exists(self.csv_path):
            return {"total": 0, "success": 0, "fail": 0, "ambiguous": 0, "accuracy": 0.0}

        stats = {"total": 0, "success": 0, "fail": 0, "ambiguous": 0}
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)  # ← استفاده از reader به جای DictReader
            for row in reader:
                if len(row) < 5:  # اگر سطر کامل نبود، رد کن
                    continue

                stats["total"] += 1

                # ستون‌ها بر اساس ایندکس:
                # 0: timestamp
                # 1: filename
                # 2: prediction
                # 3: result     ← این ستون result هست
                # 4: attempt

                result = row[3].lower()  # ← ستون چهارم (ایندکس 3)

                if result == "success":
                    stats["success"] += 1
                elif result == "fail":
                    stats["fail"] += 1
                elif result == "ambiguous":
                    stats["ambiguous"] += 1

        if stats["total"] > 0:
            stats["accuracy"] = stats["success"] / stats["total"] * 100
        else:
            stats["accuracy"] = 0.0

        return stats

    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()
        print(f"\n📊 Captcha Statistics:")
        print(f"   Total attempts: {stats['total']}")
        print(f"   Success: {stats['success']}")
        print(f"   Fail: {stats['fail']}")
        print(f"   Ambiguous: {stats['ambiguous']}")
        print(f"   Accuracy: {stats['accuracy']:.1f}%")