import pandas as pd
import requests
import time
import os
import json
import re
import csv

# Load CSV file containing locations
file_path = "../extra-csv-files/unique_last_part.csv"
df_locations = pd.read_csv(file_path, dtype=str)

# Ensure column exists and rename if necessary
if 'Last Part' not in df_locations.columns:
    df_locations.rename(columns={df_locations.columns[0]: 'Last Part'}, inplace=True)

# OpenCage API Key (Replace with your actual API key)
API_KEY = "bc7cfb5ba07c485198cf4f580fc74a87"

# Output CSV file for results
output_file_path = "opencage_location_results-unique.csv"
json_output_dir = "opencage_api_responses"

# Ensure the directory for JSON responses exists
os.makedirs(json_output_dir, exist_ok=True)

# Check if the output CSV already exists and load processed locations
if os.path.exists(output_file_path):
    existing_df = pd.read_csv(output_file_path, dtype=str)
    processed_locations = set(existing_df['location'].astype(str))
else:
    processed_locations = set()


# Function to sanitize filenames
def sanitize_filename(location):
    return re.sub(r'[<>:"/\\|?*\n]', '_', location.strip())


# Function to call OpenCage API
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

            if data.get('results'):
                first_result = data['results'][0]
                lat = first_result['geometry']['lat']
                lon = first_result['geometry']['lng']
                formatted_address = first_result.get('formatted', "")
                return location, formatted_address, lat, lon

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {location}: {e}")

    return location, "", "", ""  # Return empty fields if no data found


# Ensure CSV has a proper header
file_exists = os.path.exists(output_file_path)

with open(output_file_path, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)

    # Write headers if the file does not exist
    if not file_exists:
        writer.writerow(["location", "formatted_address", "latitude", "longitude"])

    # Skip the first 190 locations before processing
    unique_locations = df_locations['last part'].dropna().astype(str).unique()[190:]

    processed_count = 0
    for location in unique_locations:
        if location in processed_locations:
            continue  # Skip already processed locations

        # Get coordinates
        result = get_opencage_coordinates(location)

        # Save to CSV
        writer.writerow(result)
        processed_count += 1

        print(f"✅ Processed {processed_count}: {result}")

        time.sleep(1)  # Avoid hitting rate limits

print(f"✅ Location results saved to {output_file_path}")
print(f"✅ Total locations processed: {processed_count}")
print(f"✅ API responses saved in '{json_output_dir}' directory.")
