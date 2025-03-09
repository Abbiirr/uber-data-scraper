import csv
import time
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

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

# Define capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "your_device_id"  # Replace with actual device ID from `adb devices`
options.no_reset = True
options.dont_stop_app_on_reset = True

# Connect to Uber App
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("✅ Connected to Running Uber App!")

# CSV File Setup
csv_filename = "uber_price_estimates.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Pickup", "Destination", "Ride Type", "Fare", "Drop-off ETA", "Additional Info"])

# Read CSV file with locations
csv_file = "Updated_Location_Permutations.csv"
with open(csv_file, "r") as file:
    reader = csv.reader(file)
    for _ in range(245):  # Skip processed rows
        next(reader)

    for index, row in enumerate(reader, start=245):
        try:
            pickup, destination = row[0], row[1]
            print(f"🚗 Processing Route {index+1}: Pickup {pickup} -> Destination {destination}")

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
            el4.send_keys(pickup)

            # Step 5: Select first search result
            el5 = wait.until(EC.element_to_be_clickable(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("Get more results for {pickup}")')
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
            el7.send_keys(destination)

            # Step 8: Select first search result for destination
            el8 = wait.until(EC.element_to_be_clickable(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("Get more results for {destination}")')
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

            for ride in ride_elements:
                ride_details = ride.get_attribute("content-desc")
                details = ride_details.split(",")

                ride_type = details[0] if len(details) > 0 else "N/A"
                fare = details[1].replace("Fare ", "").strip() if len(details) > 1 else "N/A"
                eta = details[2].replace("estimated drop-off ", "").strip() if len(details) > 2 else "N/A"
                additional_info = ", ".join(details[3:]) if len(details) > 3 else "N/A"

                ride_data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pickup, destination, ride_type, fare, eta, additional_info])

            # Save ride data to CSV immediately
            with open(csv_filename, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(ride_data)

            # Log ride data
            for ride in ride_data:
                logging.info(f"Ride Data: {ride}")

            print("💾 Ride data saved to CSV.")

            # Step 12: Take Screenshot
            screenshot_path = f"images/uberx_route_{index+1}.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")

            # Step 13: Open Uber Menu & Go back to home
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
            error_message = f"❌ Error processing route {index+1}: {e}"
            print(error_message)
            logging.error(error_message)

# Close session
input("Press Enter to close Appium session...")
driver.quit()
