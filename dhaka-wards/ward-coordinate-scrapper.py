import os
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Constants
DATA_FILE = "dhaka_north_wards.csv"

# Ensure necessary folders exist
data_dir = os.path.dirname(DATA_FILE)
if data_dir and not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

# Create CSV file for logging ward data if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Ward Number", "Coordinates", "Zone", "Area", "Councilor"
        ])

# Set up Undetected Chrome
options = uc.ChromeOptions()
options.add_argument("--start-maximized")  # Fullscreen mode
driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)

# Base URL for Dhaka North City Corporation wards
base_url = "https://en.wikipedia.org/wiki/Ward_No._{}_({}_City_Corporation)"

# Function to extract text safely using CSS selectors
def extract_text(driver, css_selector):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        return element.text.strip()
    except Exception:
        return "N/A"

# Loop through ward numbers 1 to 43 for Dhaka North City Corporation
for ward_no in range(1, 44):
    # Construct the URL
    url = base_url.format(ward_no, "Dhaka_North")
    print(f"🔄 Fetching data for: Ward No. {ward_no}")

    # Send a GET request to the URL
    driver.get(url)

    # Extract data using CSS selectors
    coord = extract_text(driver, 'span.geo-dec')
    zone = extract_text(driver, 'th:contains("Zone") + td')
    area = extract_text(driver, 'th:contains("Area") + td')
    councilor = extract_text(driver, 'th:contains("Councilor") + td')

    # Save data to CSV
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            ward_no, coord, zone, area, councilor
        ])

    print(f"✅ Data saved for Ward No. {ward_no} | Coordinates: {coord}, Zone: {zone}, Area: {area}, Councilor: {councilor}")

# Close the driver
driver.quit()
print("🛑 Scraping completed.")
