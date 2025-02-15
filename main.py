from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define locations
start_location = "Gulshan 1, Dhaka"
end_location = "Dhanmondi 32, Dhaka"

# Path to chromedriver (Update this path)
chromedriver_path = r"K:\Softwares\chromedriver_win32\chromedriver.exe"  # Using raw string (r"")

# Set up Selenium WebDriver (Non-Headless Mode)
service = Service(chromedriver_path)
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)  # Keeps browser open
driver = webdriver.Chrome(service=service, options=options)

# Open Google Maps
driver.get("https://www.google.com/maps")

# Wait for the Directions button to load and click it
try:
    directions_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Directions')]"))
    )
    directions_button.click()
except Exception as e:
    print("Error clicking Directions button:", e)

# Enter start location
try:
    start_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Choose starting point, or click on the map...']"))
    )
    start_input.send_keys(start_location)
    start_input.send_keys(Keys.ENTER)
except Exception as e:
    print("Error entering start location:", e)

# Enter end location
try:
    end_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Choose destination']"))
    )
    end_input.send_keys(end_location)
    end_input.send_keys(Keys.ENTER)
except Exception as e:
    print("Error entering destination:", e)

# Wait for travel duration to appear
try:
    duration_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'section-directions-trip-duration')]"))
    )
    travel_time = duration_element.text
    print(f"Estimated travel time from {start_location} to {end_location}: {travel_time}")
except Exception as e:
    print("Could not retrieve travel time:", e)

# Keep browser open (Remove if you want it to close immediately)
input("Press Enter to close...")

# Close the browser
driver.quit()
