# IranModares Advertisement Auto-Updater

Automated bot for updating advertisements on [iranmodares.com](https://www.iranmodares.com). Handles login, navigation, captcha solving via ML model, and periodic updates every 20 minutes.

## Features

- **Automated Login**: Persistent browser profile maintains session
- **Smart Navigation**: Fast page loads using `wait_until="commit"` strategy
- **Captcha Solving**: CNN-based character recognition (98% accuracy)
- **Retry Logic**: Automatic retry on captcha failure (max 5 attempts)
- **Intelligent Waiting**: Parses site's own countdown text instead of fixed polling
- **Comprehensive Logging**: CSV logs every captcha attempt with screenshot
- **Error Recovery**: Graceful handling of timeouts, network errors, page changes
- **Modular Architecture**: Clean separation of concerns for easy extension

## Project Structure

```
modares/
├── config.py                 # All configuration constants
├── main.py                   # Main entry point (recommended)
├── iran2.py                  # Legacy entry point (backward compat)
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── core/                     # Core automation modules
│   ├── __init__.py
│   ├── browser.py           # Browser lifecycle management
│   ├── navigation.py        # Page navigation & interactions
│   ├── captcha.py           # Captcha handling & solving
│   ├── logger.py            # CSV logging for analysis
│   └── sound.py             # Notification sounds
├── ml/                       # Machine Learning modules
│   ├── __init__.py
│   ├── model.py             # CharCNN model definition
│   ├── predict_captcha.py   # Inference pipeline
│   ├── train.py             # Training script
│   ├── dataset.py           # Dataset handling
│   └── ...                  # Other ML utilities
└── captures/                 # Auto-generated captcha screenshots
    ├── captcha_YYYYMMDD_HHMMSS_mmm.png
    └── captcha_log.csv       # Attempt log: timestamp, file, prediction, result
```

## Requirements

- Python 3.10+
- Playwright: `pip install playwright && playwright install chromium`
- PyTorch: `pip install torch torchvision`
- OpenCV: `pip install opencv-python`
- NumPy: `pip install numpy`
- Pygame: `pip install pygame`

Or install all at once:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuration

Edit `config.py` to customize:

```python
# URLs (update if site changes)
BASE_URL = "https://www.iranmodares.com"
COMMON_INDEX_URL = f"{BASE_URL}/common-index.php?p=4"
ADVERTISEMENT_URL = f"{BASE_URL}/ControlPanel/advertisement.php?p=4"

# Credentials (use environment variables in production!)
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

# Timing
CAPTCHA_MAX_RETRIES = 5
NEXT_QUEUE_WAIT = 1250  # 20 minutes 50 seconds
MAX_WAIT_FOR_UPDATE = 1500  # Max wait for update button

# Selectors (update if site HTML changes)
SELECTORS = {
    "captcha_image": "img.item1",
    "captcha_input": 'input[name="imagecode"]',
    "captcha_submit": 'input[type="submit"].button',
    "captcha_form": 'form[name="f"]',
    ...
}
```

## Usage

### Recommended: main.py
```bash
# With profile path argument
python main.py "C:\path\to\chrome\profile"

# Or edit default in main.py and run without args
python main.py
```

### Legacy: iran2.py
```bash
python iran2.py
```

### Profile Setup
1. Create a Chrome profile directory:
   ```bash
   mkdir "C:\path\to\custom\profile"
   ```
2. First run will open browser - log in manually once
3. Session persists in profile for subsequent runs

## How It Works

### Main Loop (`main.py` → `IranModaresBot.run()`)

```
┌─────────────────────────────────────────────────────────────┐
│                    START CYCLE                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Navigate to common-index.php?p=4                        │
│     (safe_goto with commit strategy)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Click Control Panel link                                │
│     ├─ If found: proceed                                    │
│     └─ If not: Login (email/password)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Wait for Update Button                                  │
│     ├─ Go to advertisement.php?p=4                          │
│     ├─ Parse page text for countdown                        │
│     │   "هر 20 دقیقه" + "19 دقیقه پیش" → wait 65s         │
│     └─ Smart wait or poll every 60s                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Click "Go to Update" → Captcha Page                     │
│     Play alarm sound                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. CAPTCHA SOLVING LOOP (max 5 retries)                    │
│     ┌─────────────────────────────────────────────────────┐ │
│     │  a) Screenshot captcha (clip, no font wait)         │ │
│     │  b) Predict with CharCNN model                      │ │
│     │  c) Fill input[name="imagecode"]                    │ │
│     │  d) Click submit                                    │ │
│     │  e) Check result:                                   │ │
│     │     ├─ Form + captcha gone → SUCCESS ✅             │ │
│     │     ├─ Both visible → FAIL ❌ (retry)               │ │
│     │     └─ Ambiguous → FAIL ❌ (retry)                  │ │
│     └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Wait 20 min (NEXT_QUEUE_WAIT)                           │
│     Display countdown timer                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         REPEAT ◄──────────────────────────────┘
```

### Captcha Model (`ml/predict_captcha.py`)

**Architecture: CharCNN**
```
Input: 1×28×28 (grayscale character)
├─ Conv2d(1→32, 3×3, pad=1) + ReLU + MaxPool2d(2)  → 32×14×14
├─ Conv2d(32→64, 3×3, pad=1) + ReLU + MaxPool2d(2) → 64×7×7
├─ Flatten → 64×7×7 = 3136
├─ Linear(3136→128) + ReLU
└─ Linear(128→26)  → 26 classes (A-Z)
```

**Pipeline:**
1. Load image → grayscale
2. Threshold (binary inverse)
3. Find contours → bounding boxes
4. Sort left-to-right
5. Resize each char to 28×28 (centered)
6. Normalize 0-1 → tensor 1×1×28×28
7. Model inference → argmax → character
8. Concatenate all predictions

### Smart Waiting (`navigation.py`)

Instead of fixed polling, parses Persian text:
- `"امکان به روز رسانی هر 20 دقیقه یکبار فعال می باشد"` → interval = 20 min
- `"آخرین به روز رسانی شما 19 دقیقه پیش"` → elapsed = 19 min
- Remaining = (20 - 19) × 60 + 45 buffer = 105 seconds

Falls back to 60s polling if text unavailable.

## Captcha Logging (`captures/captcha_log.csv`)

| timestamp | filename | prediction | result | attempt |
|-----------|----------|------------|--------|---------|
| 20260812_143022_123 | captcha_20260812_143022_123.png | LALIO | success | 1 |
| 20260812_143500_456 | captcha_20260812_143500_456.png | ABCDE | fail | 1 |
| 20260812_143500_789 | captcha_20260812_143500_789.png | ABCDE | fail | 2 |
| 20260812_143501_012 | captcha_20260812_143501_012.png | ABCDF | success | 3 |

**Statistics available via `CaptchaLogger.print_stats()`:**
```
📊 Captcha Statistics:
   Total attempts: 150
   Success: 142
   Fail: 6
   Ambiguous: 2
   Accuracy: 94.7%
```

## Extending the Bot

### Add New Site Actions
```python
# In core/navigation.py
class Navigator:
    def new_action(self):
        # Add custom navigation logic
        pass

# Use in main.py
bot.navigator.new_action()
```

### Custom Captcha Handling
```python
# In core/captcha.py
class CaptchaSolver:
    def custom_preprocess(self, image_path):
        # Add preprocessing steps
        return processed_image
```

### Add New ML Model
```python
# In ml/predict_captcha.py
def predict_captcha(image_path, model_type="cnn"):
    if model_type == "transformer":
        return transformer_predict(image_path)
    return cnn_predict(image_path)
```

### Configuration via Environment
```python
# config.py
import os
EMAIL = os.getenv("IRANMODEARES_EMAIL", "default@email.com")
PASSWORD = os.getenv("IRANMODEARES_PASSWORD", "default_pass")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'model'` | Run from project root, ensure `ml/__init__.py` exists |
| Captcha screenshot timeout | Page not fully loaded; `commit` strategy handles this |
| Login fails | Check credentials in `config.py`; ensure profile has valid session |
| Update button never appears | Increase `MAX_WAIT_FOR_UPDATE`; check site hasn't changed |
| Model predicts wrong | Check `captures/` for failure patterns; retrain with more data |
| Browser crashes | Use persistent profile; avoid multiple instances |

## ML Model Training

```bash
# Collect data
python ml/collect.py

# Process dataset
python ml/process_dataset.py

# Train
python ml/train.py

# Evaluate
python ml/test_model.py
```

Model saves to `ml/char_cnn.pth` (referenced in `config.MODEL_PATH`).

## License

Internal use only. Do not distribute.

---

**Note**: This automation interacts with a live website. Use responsibly and respect the site's terms of service. The bot includes deliberate delays and smart waiting to minimize server load.