import os
import time
import json
import csv
import random
import requests
from datetime import datetime
from kafka import KafkaProducer

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "weather-data-meteo"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Open-Meteo API URL
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# File Paths
LOCATION_FILE = "location_pairs.csv"
DATA_FILE = "weather_data.csv"

# Ensure CSV exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Location Name", "Latitude", "Longitude", "Rain (mm)", "Temperature (°C)"])

# Read locations from CSV
def load_location_pairs():
    locations = []
    with open(LOCATION_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_coords = row["Start Coordinates"].strip().replace("(", "").replace(")", "").split(",")
            end_coords = row["End Coordinates"].strip().replace("(", "").replace(")", "").split(",")

            start_lat, start_lon = float(start_coords[0]), float(start_coords[1])
            end_lat, end_lon = float(end_coords[0]), float(end_coords[1])

            start_name = row["Start Location Name"].strip()
            end_name = row["End Location Name"].strip()

            locations.append((start_name, start_lat, start_lon))
            locations.append((end_name, end_lat, end_lon))  # Both start and end locations

    return locations

# Get closest time index within ±20 minutes
def find_closest_weather_data(weather_data):
    hourly_times = weather_data["hourly"]["time"]
    rain_values = weather_data["hourly"]["rain"]
    temp_values = weather_data["hourly"]["temperature_2m"]

    # Convert timestamps to datetime objects
    time_format = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow()
    closest_time = None
    closest_rain = 0.0
    closest_temp = None

    for idx, timestamp in enumerate(hourly_times):
        forecast_time = datetime.strptime(timestamp, time_format)
        time_diff = abs((forecast_time - current_time).total_seconds())

        if time_diff <= 1200:  # 1200 seconds = 20 minutes
            closest_time = forecast_time
            closest_rain = rain_values[idx]
            closest_temp = temp_values[idx]
            break

    return closest_time, closest_rain, closest_temp

# Load locations
locations = load_location_pairs()
print(f"✅ Loaded {len(locations)} unique locations from {LOCATION_FILE}")

try:
    while True:
        for location_name, lat, lon in locations:
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "rain,temperature_2m",
                "timezone": "auto"
            }

            response = requests.get(WEATHER_API_URL, params=params)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch data for {location_name}")
                continue

            weather_data = response.json()
            closest_time, rain, temperature = find_closest_weather_data(weather_data)

            if closest_time:
                timestamp = closest_time.strftime("%Y-%m-%d %H:%M:%S")

                # Save data to CSV
                with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, location_name, lat, lon, rain, temperature])

                print(f"✅ Logged weather for {location_name}: Rain={rain} mm, Temp={temperature}°C at {timestamp}")

                # Send data to Kafka
                kafka_message = {
                    "timestamp": timestamp,
                    "location_name": location_name,
                    "latitude": lat,
                    "longitude": lon,
                    "rain": rain,
                    "temperature": temperature
                }

                producer.send(KAFKA_TOPIC, value=kafka_message)
                producer.flush()
                print(f"🚀 Published to Kafka: {kafka_message}")

            else:
                print(f"⚠️ No valid data available within ±20 minutes for {location_name}")

            # Random delay (5-10 minutes)
            wait_time = random.randint(300, 600)
            print(f"⏳ Waiting {wait_time // 60} minutes...\n")
            time.sleep(wait_time)

except KeyboardInterrupt:
    print("🛑 Stopping script...")
    producer.close()
