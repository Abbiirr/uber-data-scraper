from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "your_device_id"  # Replace with your actual device ID from `adb devices`
options.no_reset = True  # Ensures the app does not reset
options.dont_stop_app_on_reset = True  # Keeps Uber running

# Attach to the running Uber app
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("✅ Connected to Running Uber App!")

try:
    wait = WebDriverWait(driver, 10)

    # Step 1: Tap on "Enter destination"
    el1 = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Enter destination")))
    el1.click()

    # Step 2: Select pickup location
    el2 = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "pickup location  1206 Manikdi Bazar Road")))
    el2.click()

    # Step 3: Click on the pickup location selection button (Edit icon)
    el3 = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.ubercab:id/image_view")))
    el3.click()

    # Step 4: Enter new pickup location coordinates
    el4 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))
    el4.send_keys("23.7915995,90.4167872")

    # Step 5: Select the first search result
    el5 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Get more results for 23.7915995,90.4167872")')))
    el5.click()

    # Step 6: Confirm pickup location
    el6 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')))
    el6.click()

    # Step 7: Click on the destination entry field
    el7 = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.ubercab:id/edit_text")))
    el7.click()
    el7.send_keys("23.8493,90.3978")

    # Step 8: Select the first search result for the destination
    el8 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Get more results for 23.8493,90.3978")')))
    el8.click()

    # Step 9: Confirm destination
    el9 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.ImageView").instance(2)')))
    el9.click()

    # Wait for ride options to appear
    print("⏳ Fetching Ride Estimates...")
    time.sleep(5)

    # Select UberX first
    try:
        el_uberx = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "selected,UberX")
        el_uberx.click()
        print("✅ UberX selected successfully!")
    except Exception as e:
        print(f"❌ Error selecting UberX: {e}")

    import time

    # Attempt to select UberX
    try:
        el_uberx = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "selected,UberX")
        el_uberx.click()
        print("✅ UberX selected successfully!")

    except Exception as e:
        print(f"⚠️ Could not select UberX: {e}")

    # Always take a screenshot
    screenshot_path = f"uberx_selection_{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    print(f"📸 Screenshot saved: {screenshot_path}")

    # except Exception as e:
    #     print(f"❌ Error extracting estimates: {e}")

    # Step 10: Open Uber Menu
    el10 = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Menu")))
    el10.click()

    # Step 11: Go back to home screen
    el11 = wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Back")')))
    el11.click()

except Exception as e:
    print(f"❌ Error: {e}")

# Close the session
input("Press Enter to close Appium session...")
driver.quit()
