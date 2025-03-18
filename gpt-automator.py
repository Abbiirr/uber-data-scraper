import time
import json
import random
import os
import shutil
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load and clean the CSV
file_path = "unique_pickup_points.csv"
try:
    df = pd.read_csv(file_path, names=["Location"], skiprows=1)  # Skip header if needed
    df["Location"] = df["Location"].str.strip().str.replace('"', '')
    print(f"✅ Loaded {len(df)} locations from CSV.")
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit(1)

# Set download directory
DOWNLOAD_DIR = os.path.join(os.getcwd(), "chatgpt_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Start undetected Chrome
try:
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,  # Set download location
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    driver = uc.Chrome(options=options)
    print("✅ Browser initiated successfully.")
except Exception as e:
    print(f"❌ Error starting browser: {e}")
    exit(1)

# Open ChatGPT and wait for manual login
driver.get("https://chat.openai.com")

print("🔑 Please log in to ChatGPT manually (30 seconds).")
time.sleep(30)  # Fixed wait for manual login
print("✅ Proceeding after manual login...")


def send_prompt(prompt):
    """ Sends a batch of locations as a single prompt to ChatGPT and downloads files if available. """
    try:
        # Find and focus on the input field
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "prompt-textarea"))
        )

        input_box.click()  # Ensure focus before typing

        # Clear the field (in case it has placeholder text)
        input_box.send_keys(Keys.CONTROL + "a")
        input_box.send_keys(Keys.DELETE)

        # Send the message directly using send_keys()
        input_box.send_keys(prompt)

        # Find and click the send button
        send_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-button']"))
        )
        send_button.click()

        print(f"✉️ Sent prompt with {prompt.count('\n') + 1} locations.")

        # Wait for the stop generation button to appear first (means generation started)
        try:
            stop_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Stop generating']"))
            )
            print("⏳ Response generation started...")

            # Now wait for the stop button to disappear and the regenerate button to appear
            # This means the message is fully generated
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='regenerate-button']"))
            )

            # Extra wait to ensure everything is loaded
            time.sleep(1)

            # Extract last response
            responses = driver.find_elements(By.CSS_SELECTOR, "div.markdown.prose")
            if responses:
                response = responses[-1].text
                print(f"💬 Response Received ({len(response)} characters)")

                # Check and download files
                check_and_download_files()

                return response
            else:
                print("⚠️ No response elements found")
                return None

        except TimeoutException:
            print("⚠️ Timeout waiting for response or regenerate button")
            return None

    except Exception as e:
        print(f"⚠️ Error during prompt submission: {e}")
        return None


def check_and_download_files():
    """ Checks for available file downloads and saves them. """
    try:
        # Find all possible download buttons
        download_buttons = driver.find_elements(By.CSS_SELECTOR,
                                                "a[href$='.zip'], a[href$='.csv'], a[href$='.txt'], a[href$='.pdf']")

        if not download_buttons:
            print("❌ No files detected for download.")
            return

        for button in download_buttons:
            file_url = button.get_attribute("href")
            if file_url:
                print(f"📥 Downloading file: {file_url}")
                driver.get(file_url)  # Click the link to initiate the download
                time.sleep(5)  # Allow time for download to start

        # Move downloaded files to a separate folder
        move_downloaded_files()

    except Exception as e:
        print(f"⚠️ Error while checking or downloading files: {e}")


def move_downloaded_files():
    """ Moves downloaded files to a separate folder after download. """
    time.sleep(5)  # Ensure file is completely downloaded
    for file_name in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, file_name)
        if os.path.isfile(file_path):
            new_location = os.path.join(DOWNLOAD_DIR, "processed_" + file_name)
            shutil.move(file_path, new_location)
            print(f"📂 Moved downloaded file to: {new_location}")


def process_csv_in_batches(df, batch_size=50):
    """ Reads the CSV in batches and loops indefinitely """
    total_batches = (len(df) + batch_size - 1) // batch_size

    while True:
        for i in range(0, len(df), batch_size):
            batch_num = (i // batch_size) + 1
            print(f"🔄 Processing batch {batch_num}/{total_batches}")

            batch = df.iloc[i:i + batch_size]["Location"].tolist()
            prompt = "Process these locations:\n\n" + "\n".join(batch)

            response = send_prompt(prompt)
            if response:
                # Optional: save responses to a file
                with open(f"responses_batch_{batch_num}.txt", "w", encoding="utf-8") as f:
                    f.write(response)

            # Add random delay between requests to avoid detection
            delay = random.uniform(55, 70)
            print(f"⏱️ Waiting {delay:.1f} seconds before next batch...")
            time.sleep(delay)

        print("🔄 Completed full CSV cycle. Starting over...")
        time.sleep(5)


try:
    # Start the loop
    process_csv_in_batches(df, batch_size=50)
except KeyboardInterrupt:
    print("👋 Script interrupted by user.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    # Keep browser open for manual inspection
    input("Press Enter to close the browser...")
    driver.quit()
