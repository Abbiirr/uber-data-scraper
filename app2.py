import csv
import time
import random
import os
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import subprocess
import uuid

# Setup logging
log_filename = "uber_routes.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, mode="a"),
        logging.StreamHandler()
    ]
)

# Function to fetch the device ID dynamically
def get_device_id():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            device_id = lines[1].split("\t")[0]  # Extract the first connected device ID
            return device_id if device_id else "unknown_device"
    except Exception as e:
        print(f"❌ Could not fetch device ID: {e}")
        return "unknown_device"

device_id = get_device_id()

# Define capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = device_id
options.no_reset = True
options.dont_stop_app_on_reset = True

# Connect to Uber App
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("✅ Connected to Running Uber App!")

# Set dynamic filenames
csv_filename = f"{device_id}_uber_estimates.csv"

# CSV File Setup
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Unique ID", "Timestamp", "Device Name", "Pickup Coordinates", "Destination Coordinates",
                     "Start Location Name", "End Location Name", "Info", "Image Name"])

# Read CSV file with locations and randomize order
csv_file = "location_pairs.csv"
with open(csv_file, "r") as file:
    reader = csv.reader(file)
    routes = list(reader)

# Remove header
header = routes.pop(0)

# Shuffle the route order
random.shuffle(routes)

for index, row in enumerate(routes, start=1):
    try:
        # Generate a unique ID
        unique_id = str(uuid.uuid4())

        # Extract and clean values
        pickup_coords = row[0].strip('"()')  # Remove parentheses and quotes
        destination_coords = row[1].strip('"()')
        start_location_name = row[2]
        end_location_name = row[3]

        print(f"🚗 Processing Route {index}: {start_location_name} -> {end_location_name} ({pickup_coords} -> {destination_coords})")

        wait = WebDriverWait(driver, 10)

        # Step 1: Tap "Enter destination"
        el1 = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Enter destination")))
        el1.click()

        # Step 2: Select pickup
        el2 = wait.until(EC.presence_of_element_located(
            (AppiumBy.XPATH, "//android.widget.TextView[starts-with(@content-desc, 'pickup location ')]")
        ))
        el2.click()

        # Step 3: Confirm pickup
        el3 = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.ubercab:id/image_view")))
        el3.click()

        # Step 4: Enter new pickup coordinates
        el4 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))
        el4.clear()
        el4.send_keys(pickup_coords)

        # Step 5: Select first search result
        el5 = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("Get more results for {pickup_coords}")')
        ))
        el5.click()

        # Step 6: Confirm pickup location
        el6 = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')
        ))
        el6.click()

        # Step 7: Enter destination
        el7 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))
        el7.click()
        el7.send_keys(destination_coords)

        # Step 8: Select first search result for destination
        el8 = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("Get more results for {destination_coords}")')
        ))
        el8.click()

        # Step 9: Confirm destination
        el9 = wait.until(EC.element_to_be_clickable(
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')
        ))
        el9.click()

        # Step 10: Wait for ride options
        print("⏳ Fetching Ride Estimates...")
        time.sleep(5)

        # Step 11: Extract Ride Information
        ride_data = []
        ride_elements = driver.find_elements(AppiumBy.XPATH, "//android.view.View[contains(@content-desc, 'Fare')]")

        # Ensure directory for screenshots exists
        screenshot_dir = f"{device_id}_images"
        os.makedirs(screenshot_dir, exist_ok=True)

        # Generate timestamp for screenshot filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"{screenshot_dir}/{device_id}_uberx_route_{index}_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")

        for ride in ride_elements:
            ride_details = ride.get_attribute("content-desc").strip()
            ride_data.append([
                unique_id,  # Unique ID added at the start
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device_id,
                pickup_coords, destination_coords,
                start_location_name, end_location_name,
                ride_details, screenshot_path
            ])

        # Save ride data to CSV immediately
        with open(csv_filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(ride_data)

        # Log ride data
        for ride in ride_data:
            logging.info(f"Ride Data: {ride}")

        print("💾 Ride data saved to CSV.")

        # Step 12: Open Uber Menu & Go back to home
        try:
            el10 = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Menu")))
            el10.click()

            el11 = wait.until(EC.element_to_be_clickable(
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Back")')
            ))
            el11.click()
        except:
            print("⚠️ Unable to navigate back to home.")

    except Exception as e:
        error_message = f"❌ Error processing route {index}: {e}"
        print(error_message)
        logging.error(error_message)

# Close session
input("Press Enter to close Appium session...")
driver.quit()
