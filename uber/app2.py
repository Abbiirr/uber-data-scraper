import csv
import time
import random
import os
import subprocess
import uuid
import json
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from kafka import KafkaProducer

KAFKA_BROKER = "172.16.231.135:31000"
KAFKA_TOPIC = "uber-data-scrap-raw"

# Setup logging
log_filename = "../uber_routes.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename, mode="a", encoding="utf-8"), logging.StreamHandler()]
)


# Fetch device ID dynamically
def get_device_id():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            return lines[1].split("\t")[0] or "unknown_device"
    except Exception as e:
        logging.error(f"❌ Could not fetch device ID: {e}")
    return "unknown_device"


device_id = get_device_id()

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Define capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = device_id
options.no_reset = True
options.dont_stop_app_on_reset = True

# Connect to Uber App
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
logging.info("✅ Connected to Running Uber App!")

# Set dynamic filenames
csv_filename = f"{device_id}_uber_estimates.csv"

# CSV Setup
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Unique ID", "Timestamp", "Device Name", "Pickup Coordinates", "Destination Coordinates",
                     "Start Location Name", "End Location Name", "Info", "Image Name"])

# Read and shuffle routes
with open("../extra-csv-files/location_pairs_with_dummy_coordinates.csv", "r") as file:
    routes = list(csv.reader(file))

routes.pop(0)  # Remove header
random.shuffle(routes)

# Ensure screenshot directory exists
screenshot_dir = f"{device_id}_images"
os.makedirs(screenshot_dir, exist_ok=True)


# Fallback: Go back if stuck
def go_back():
    """Attempts to navigate back and waits for the home screen to load."""
    try:
        back_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Back")')
        back_btn.click()
        logging.info("🔙 Navigated back successfully.")
    except NoSuchElementException:
        logging.warning("⚠️ 'Back' button not found. Using device back button.")
        driver.back()

    # ✅ Wait for "Enter destination" to appear before continuing
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Enter destination"))
        )
        logging.info("🏠 Uber home page detected. Continuing...")
    except TimeoutException:
        logging.error("⚠️ Uber home page not detected after going back! It may be stuck.")


# Perform action with fallback
def perform_action(by, locator, action="click", value=None, timeout=10):
    """
    Performs an action (click or send_keys) on a UI element with fallback handling.
    Waits for the element to be present before acting.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        if action == "click":
            element.click()
        elif action == "send_keys" and value:
            element.clear()
            element.send_keys(value)
        return True
    except TimeoutException:
        logging.error(f"❌ Timeout: Element {locator} not found after {timeout} seconds. Retrying once...")

        # Retry once after waiting 3 extra seconds
        time.sleep(3)
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            if action == "click":
                element.click()
            elif action == "send_keys" and value:
                element.clear()
                element.send_keys(value)
            logging.info(f"✅ Element {locator} found on retry.")
            return True
        except TimeoutException:
            logging.error(f"❌ Element {locator} still not found after retry. Going back...")
            go_back()
            return False


def is_element_present(by, locator, timeout=5):
    """Check if an element exists within a given timeout."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        return True  # ✅ Element exists
    except TimeoutException:
        return False  # ❌ Element not found

surge_price_xpaths = [
    '//android.widget.TextView[@content-desc="Fares are slightly higher due to increased demand"]',
    '//android.widget.TextView[@content-desc="Fares are higher due to increased demand"]'
]

def is_surge_pricing():
    """Checks if surge pricing message is displayed."""
    for xpath in surge_price_xpaths:
        if is_element_present(AppiumBy.XPATH, xpath):
            return True  # ✅ Surge pricing detected
    return False  # ❌ No surge pricing

# Process routes
for index, row in enumerate(routes, start=1):
    try:
        unique_id = str(uuid.uuid4())
        pickup_coords, destination_coords, start_location_name, end_location_name = map(str.strip, row)

        logging.info(f"🚗 Processing Route {index}: {start_location_name} -> {end_location_name}")

        # Step 1: Tap "Enter destination"
        if not perform_action(AppiumBy.ACCESSIBILITY_ID, "Enter destination"):
            continue

        # Step 2: Select pickup location
        if not perform_action(AppiumBy.ID, "com.ubercab:id/ub__location_edit_search_pickup_view"):
            continue

        # Step 3: Confirm pickup
        if not perform_action(AppiumBy.ID, "com.ubercab:id/image_view"):
            continue

        # Step 4: Enter pickup coordinates
        if not perform_action(AppiumBy.ID, "com.ubercab:id/edit_text", "send_keys", start_location_name):
            continue

        # Step 5: Select pickup location from suggestions
        if not perform_action(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{start_location_name}")'):
            continue

        # Step 6: Confirm pickup location
        if not perform_action(AppiumBy.ANDROID_UIAUTOMATOR,
                              'new UiSelector().className("android.widget.LinearLayout").instance(19)'):
            continue

        # Step 7: Enter destination
        if not perform_action(AppiumBy.ID, "com.ubercab:id/edit_text", "send_keys", end_location_name):
            continue

        # Step 8: Select destination from suggestions
        if not perform_action(AppiumBy.ANDROID_UIAUTOMATOR,
                              'new UiSelector().className("android.widget.LinearLayout").instance(19)'):
            continue

        logging.info("⏳ Fetching Ride Estimates...")

        try:
            # ✅ Wait up to 10 seconds for at least one ride option to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//android.view.View[contains(@content-desc, 'Fare')]"))
            )
            logging.info("✅ Ride Estimates Loaded Successfully.")
        except TimeoutException:
            logging.error("❌ Ride Estimates did not load in time. Skipping this route.")
            go_back()
            continue  # Skip to the next route

        # Detect surge pricing before extracting ride information
        is_surge_price = is_surge_pricing()

        if is_surge_price:
            logging.warning("⚠️ Surge Pricing Alert Detected!")
        else:
            logging.info("✅ No surge pricing message detected.")

        # Step 9: Extract ride information
        ride_data = []
        ride_elements = driver.find_elements(AppiumBy.XPATH, "//android.view.View[contains(@content-desc, 'Fare')]")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"{screenshot_dir}/{device_id}_uberx_route_{index}_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"📸 Screenshot saved: {screenshot_path}")

        for ride in ride_elements:
            ride_entry = {
                "uniqueId": unique_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "deviceName": device_id,
                "pickupCoordinates": pickup_coords,
                "destinationCoordinates": destination_coords,
                "startLocation": start_location_name,
                "endLocation": end_location_name,
                "info": ride.get_attribute("content-desc").strip(),
                "imagePath": screenshot_path,
                "is_surge_price": is_surge_price  # ✅ New field added
            }
            ride_data.append(ride_entry)
            producer.send(KAFKA_TOPIC, value=ride_entry)
            logging.info(f"🚀 Published to Kafka: {ride_entry}")

        # Save to CSV
        with open(csv_filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for ride in ride_data:
                writer.writerow(ride.values())

        logging.info("💾 Ride data saved and published to Kafka.")

        # Step 10: Open Uber Menu & Go back to home
        if not perform_action(AppiumBy.ACCESSIBILITY_ID, "Menu"):
            continue
        if not perform_action(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Back")'):
            continue

    except Exception as e:
        logging.error(f"❌ Error processing route {index}: {e}")
        driver.save_screenshot(f"{screenshot_dir}/error_{index}.png")

# Close session
input("Press Enter to close Appium session...")
driver.quit()
producer.close()
