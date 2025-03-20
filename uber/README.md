# Uber Data Scraping

## Prerequisites

Ensure you have the following installed on your system:

- Android SDK
- Node.js
- Appium
- Appium UI Automator2 Driver
- Python

## Installation and Setup

### Step 1: Install Android SDK on Your Device

1. Download and install the Android SDK from [Android Developer](https://developer.android.com/studio).
2. Set the `ANDROID_HOME` environment variable:
   - On Windows:
     ```sh
     setx ANDROID_HOME "C:\path\to\Android\Sdk"
     ```
   - On macOS/Linux:
     ```sh
     export ANDROID_HOME=/path/to/Android/Sdk
     export PATH=$ANDROID_HOME/platform-tools:$PATH
     ```

### Step 2: Install Node.js

Download and install Node.js from [Node.js Official Website](https://nodejs.org/).

### Step 3: Install Appium and UI Automator2 Driver

Run the following commands:

```sh
npm install -g appium
npm install -g appium-uiautomator2-driver
appium driver install uiautomator2

```

### Step 4: Install Python Dependencies

Ensure you have Python installed, then install the required dependencies:

```sh
pip install -r requirements.txt
```

### Step 5: Start Appium Server

```sh
appium
```

### Step 6: Connect Mobile Device

1. Enable USB Debugging on your Android device:
   - Go to **Settings** > **About phone** > Tap **Build number** multiple times to enable Developer Mode.
   - Navigate to **Developer options** and enable **USB Debugging**.
2. Connect your device via USB and allow the debugging connection when prompted.
3. Verify device connection:
   ```sh
   adb devices
   ```
   Ensure your device is listed.

### Step 7: Run the Automation Script

Execute the Python script:

```sh
python app2.py
```

### Step 8: Check Captured Data

1. The CSV file with ride estimates will be saved as:
   ```sh
   {device_id}_uber_estimates.csv
   ```
2. Screenshots will be saved under a directory named after your device ID:
   ```sh
   {device_id}_images/
   ```

## Troubleshooting

- If `adb devices` does not list your device:
  - Ensure USB Debugging is enabled.
  - Try running `adb kill-server` and `adb start-server`.
  - Check for necessary USB drivers (Windows users may need to install Android USB drivers).
- If Appium fails to start, ensure Node.js and dependencies are properly installed.
- If the script fails to find elements, ensure your Uber app is updated and UI selectors are correct.

## License

This project is licensed under the MIT License.

