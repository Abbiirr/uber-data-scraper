import pandas as pd
import requests
import time
import os
import json
import re

# Load CSV file safely
file_path = "unique_locations.csv"
df_locations = pd.read_csv(file_path)

# Ensure column exists and rename if necessary
if 'location' not in df_locations.columns:
    df_locations.rename(columns={df_locations.columns[0]: 'location'}, inplace=True)

# OpenCage API Key
API_KEY = "b9233035609a472c9f1a7a5e39cabfc7"

# Output CSV file
output_file_path = "locations_with_coordinates-open-cage.csv"
json_output_dir = "api_responses"

# Ensure the directory for JSON responses exists
os.makedirs(json_output_dir, exist_ok=True)

# Load existing data if the file exists
if os.path.exists(output_file_path):
    existing_df = pd.read_csv(output_file_path)

    # Ensure the column name is correct
    if existing_df.columns[0] != 'location':
        existing_df.rename(columns={existing_df.columns[0]: 'location'}, inplace=True)

    processed_locations = set(existing_df['location'].astype(str))
    processed_count = len(existing_df)
else:
    processed_locations = set()
    processed_count = 0

# Function to sanitize filenames
def sanitize_filename(location):
    return re.sub(r'[<>:"/\\|?*]', '_', location.strip())

# Function to get coordinates from OpenCage API (No retries)
def get_opencage_coordinates(location):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location},Bangladesh&key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Save API response
            json_filename = os.path.join(json_output_dir, f"{sanitize_filename(location)}.json")
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4)

            if data['results']:
                lat = data['results'][0]['geometry']['lat']
                lon = data['results'][0]['geometry']['lng']
                return (lat, lon)
            else:
                print(f"❌ No coordinates found for: {location}")
                return "not found"
        else:
            print(f"❌ Error fetching {location}: {response.status_code}")
            return "not found"

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {location}: {e}")
        return "not found"

# Open CSV file in append mode
with open(output_file_path, "a", encoding="utf-8") as f:
    for location in df_locations['location'].dropna().astype(str).unique():
        if location in processed_locations:
            continue

        coords = get_opencage_coordinates(location)
        if coords == "not found":
            f.write(f'"{location}","not found"\n')  # Write "not found" if no coordinates are available
        else:
            f.write(f'"{location}","({coords[0]}, {coords[1]})"\n')  # Save successful coordinates

        processed_count += 1
        print(f"✅ Processed {processed_count}: {location} -> {coords}")

        time.sleep(1)  # Avoid hitting rate limits

print(f"✅ Geocoded locations saved to {output_file_path}")
print(f"✅ Total locations processed: {processed_count}")
print(f"✅ API responses saved in '{json_output_dir}' directory.")
