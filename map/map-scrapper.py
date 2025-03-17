import os
import time
import csv
import random
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from kafka import KafkaProducer  # Import Kafka producer

# Kafka configuration
KAFKA_BROKER = "localhost:9092"  # Change this if needed
KAFKA_TOPIC = "gmaps-data-scrap"  # Kafka topic for Google Maps data

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Ensure messages are JSON-encoded
)

# Constants
LOCATION_FILE = "../uber/location_pairs.csv"
DATA_FILE = "../traffic_data.csv"
SCREENSHOT_FOLDER = "map_ss"

# Ensure necessary folders exist
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

# Read location pairs from CSV
def load_location_pairs():
    locations = []
    with open(LOCATION_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_coords = row["Start Coordinates"].strip().replace("(", "").replace(")", "")
            end_coords = row["End Coordinates"].strip().replace("(", "").replace(")", "")
            start_name = row["Start Location Name"].strip()
            end_name = row["End Location Name"].strip()
            locations.append((start_coords, end_coords, start_name, end_name))
    return locations

# Create CSV file for logging traffic data if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp", "Start Location Name", "End Location Name",
            "Start Coordinates", "End Coordinates",
            "Travel Time", "Distance", "Screenshot"
        ])

# Set up Undetected Chrome
options = uc.ChromeOptions()
options.add_argument("--start-maximized")  # Fullscreen mode
driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)

# Load locations
locations = load_location_pairs()
if not locations:
    print("⚠️ No location pairs found in", LOCATION_FILE)
    driver.quit()
    exit()

print(f"✅ Loaded {len(locations)} location pairs.")

try:
    while True:
        for start_coords, end_coords, start_name, end_name in locations:
            # Construct Google Maps URL
            url = f"https://www.google.com/maps/dir/{start_coords}/{end_coords}/data=!4m2!4m1!3e0"
            driver.get(url)
            time.sleep(10)  # Allow page to load

            print(f"🔄 Fetching data for: {start_name} → {end_name}")

            # Initialize values
            travel_time, distance = "N/A", "N/A"

            # Try extracting travel time
            try:
                travel_time_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#section-directions-trip-0 > div.MespJc > div > div.XdKEzd > div.Fk3sm.fontHeadlineSmall[class*='delay-']"))
                )
                travel_time = travel_time_element.text.strip()
            except Exception:
                print("⚠️ Could not extract Travel Time.")

            # Try extracting distance
            try:
                distance_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#section-directions-trip-0 > div.MespJc > div > div.XdKEzd > div.ivN21e.tUEI8e.fontBodyMedium > div"))
                )
                distance = distance_element.text.strip()
            except Exception:
                print("⚠️ Could not extract Distance.")

            # Generate timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # If extraction fails, save screenshot
            screenshot_path = "N/A"
            if travel_time == "N/A" or distance == "N/A":
                screenshot_filename = f"traffic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                screenshot_path = os.path.join(SCREENSHOT_FOLDER, screenshot_filename)
                driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")

            # Save data to CSV
            with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp, start_name, end_name, start_coords, end_coords,
                    travel_time, distance, screenshot_path
                ])

            print(f"✅ Data saved: {start_name} → {end_name} | Time: {travel_time}, Distance: {distance}")

            # Prepare message for Kafka
            kafka_message = {
                "timestamp": timestamp,
                "start_location_name": start_name,
                "end_location_name": end_name,
                "start_coordinates": start_coords,
                "end_coordinates": end_coords,
                "travel_time": travel_time,
                "distance": distance,
                "screenshot_path": screenshot_path
            }

            # Send message to Kafka
            producer.send(KAFKA_TOPIC, value=kafka_message)
            producer.flush()  # Ensure immediate publishing
            print(f"🚀 Published to Kafka: {kafka_message}")

            # Random wait time between 5 to 10 minutes
            wait_time = random.randint(300, 600)  # Random seconds between 5 and 10 minutes
            print(f"⏳ Waiting {wait_time // 60} minutes before switching to next location...\n")
            time.sleep(wait_time)

except KeyboardInterrupt:
    print("🛑 Stopping script...")
    driver.quit()
    producer.close()
