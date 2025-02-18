# Iranmodares Automation Script

This is a Python script designed to automate certain tasks on the [Iranmodares](https://www.iranmodares.com) website. It uses Selenium for browser automation and includes features like login, navigation, and handling captcha.

---

## 🚀 Features

- **Automatic Login**: Logs into the Iranmodares website using provided credentials.
- **Page Navigation**: Navigates to specific pages and interacts with elements.
- **Captcha Handling**: Prompts the user to solve captcha manually.
- **Sound Notification**: Plays a sound alert when user interaction is required.
- **Countdown Timer**: Includes a countdown timer for waiting between tasks.

---

## ⚙️ Requirements

To run this script, you need the following:

- **Python 3.7 or higher**
- **Selenium**: Install via `pip install selenium`
- **ChromeDriver**: Download the version compatible with your Chrome browser from [here](https://sites.google.com/chromium.org/driver/).
- **Pygame**: Install via `pip install pygame` (for sound notifications).

---

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/jazavaja/iranmodares.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download ChromeDriver and place it in your system's PATH or specify its location in the script.

---

## 🖥️ Usage

1. Update the `profile_path` variable in the script with the path to your Chrome user profile (optional).
2. Run the script:
   ```bash
   python iran.py
   ```

3. Follow the on-screen instructions:
   - The script will attempt to log in automatically.
   - If a captcha is encountered, you will be prompted to solve it manually.
   - A sound alert will notify you when your input is required.

---

## 🧩 Code Structure

- **`Iranmodares` Class**: Contains all the main functionality, including login, navigation, and captcha handling.
- **`init_driver` Method**: Initializes the Chrome WebDriver with custom options.
- **`doLogin` Method**: Handles the login process.
- **`go_to_update` Method**: Navigates to the update page and handles captcha.
- **`play_sound` Method**: Plays a sound alert using Pygame.
- **`wait_until_ready` Method**: Implements a countdown timer.

---

## ⚠️ Important Notes

- **Captcha Handling**: This script cannot solve captchas automatically. You will need to solve them manually when prompted.
- **ChromeDriver Compatibility**: Ensure that the version of ChromeDriver matches your installed Chrome browser version.
- **User Profile**: Using a custom Chrome profile is optional but recommended for saving session data.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Thanks to the Selenium team for their amazing browser automation tools.
- Special thanks to the Pygame community for providing sound functionality.

---

## 📧 Contact

If you have any questions or suggestions, feel free to reach out:

- **Email**: javadesmesh@gmail.com
- **GitHub**: [jazavaja](https://github.com/jazavaja)

---
