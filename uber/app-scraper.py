import csv
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Setup logging
log_filename = "../uber_routes.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, mode="a"),  # Save logs to a file
        logging.StreamHandler()  # Print logs to console
    ]
)
# Define capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "your_device_id"  # Replace with actual device ID from `adb devices`
options.no_reset = True  # Ensures the app does not reset
options.dont_stop_app_on_reset = True  # Keeps Uber running

# Attach to the running Uber app
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("✅ Connected to Running Uber App!")

# Read CSV file
csv_file = "../Updated_Location_Permutations.csv"  # Ensure the CSV file is in the same directory
with open(csv_file, "r") as file:
    reader = csv.reader(file)
    # Skip first 15 rows (since index starts from 0)
    for _ in range(245):
        next(reader)

    for index, row in enumerate(reader, start=245):
        try:
            pickup, destination = row[0], row[1]
            print(f"🚗 Processing Route {index+1}: Pickup {pickup} -> Destination {destination}")

            wait = WebDriverWait(driver, 10)

            # Step 1: Tap on "Enter destination"
            el1 = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Enter destination")))
            el1.click()

            # Step 2: Click on pickup location
            el2 = wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//android.widget.TextView[starts-with(@content-desc, 'pickup location ')]")
            ))
            el2.click()

            # Step 3: Click on the pickup selection button
            el3 = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.ubercab:id/image_view")))
            el3.click()

            # Step 4: Enter new pickup coordinates
            # Step 4: Enter new pickup coordinates
            el4 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))
            el4.click()  # Ensure the field is focused
            el4 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))  # Re-fetch
            el4.clear()  # Clear previous text
            el4.send_keys(pickup)  # Enter new coordinates

            # Step 5: Select first search result
            el5 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("Get more results for {pickup}")')))
            el5.click()

            # Step 6: Confirm pickup location
            el6 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')))
            el6.click()

            # Step 7: Click on destination entry field
            el7 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))
            el7.click()
            el7.send_keys(destination)

            # Step 8: Select first search result for destination
            el8 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("Get more results for {destination}")')))
            el8.click()

            # Step 9: Confirm destination
            el9 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')))
            el9.click()

            # Wait for ride options to appear
            print("⏳ Fetching Ride Estimates...")
            time.sleep(5)

            # Step 10: Select UberX
            try:
                el_uberx = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "selected,UberX")
                el_uberx.click()
                print("✅ UberX selected successfully!")
            except Exception as e:
                print(f"⚠️ Could not select UberX: {e}")

            # Step 11: Take Screenshot
            screenshot_path = f"images/uberx_route_{index+1}.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")

            # Step 12: Open Uber Menu
            el10 = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Menu")))
            el10.click()

            # Step 13: Go back to home screen
            el11 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Back")')))
            el11.click()

        except Exception as e:
            print(f"❌ Error processing route {index+1}: {e}")

# Close the session
input("Press Enter to close Appium session...")
driver.quit()
