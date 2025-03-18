import pandas as pd
import requests
import time
import os
import json
import re
import csv

# Load CSV file containing locations
file_path = "unique_last_part.csv"
df_locations = pd.read_csv(file_path, dtype=str)

# Ensure column exists and rename it
if 'Last Part' not in df_locations.columns:
    df_locations.rename(columns={df_locations.columns[0]: 'Last Part'}, inplace=True)

# Barikoi API Key (Replace with your actual key)
API_KEY = "bkoi_daaf88c294362d1b0e0c3f29b96b64477ee293407221fdd6657c792f104b09c6"

# Output CSV file for results
output_file_path = "barikoi_location_results-3.csv"
json_output_dir = "barikoi_api_responses"

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


# Function to call Barikoi API
def get_barikoi_data(location):
    url = f"https://barikoi.xyz/v2/api/search/autocomplete/place?api_key={API_KEY}&q={location}&city=dhaka&sub_area=true&sub_district=true"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Save API response
            json_filename = os.path.join(json_output_dir, f"{sanitize_filename(location)}.json")
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4)

            return data  # Return full JSON response
        else:
            print(f"⚠️ API returned non-200 status for {location}: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {location}: {e}")

    return None  # Return None if no valid data found


# Ensure CSV has a proper header
file_exists = os.path.exists(output_file_path)

with open(output_file_path, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)

    # Write headers if the file does not exist
    if not file_exists:
        writer.writerow(["location", "address", "area", "city", "longitude", "latitude"])

    # Skip the first 190 locations before processing
    unique_locations = df_locations['Last Part'].dropna().astype(str).unique()[190:]

    processed_count = 0
    for location in unique_locations:
        if location in processed_locations:
            continue  # Skip already processed locations

        data = get_barikoi_data(location)

        # Extract relevant fields
        if data and 'places' in data and len(data['places']) > 0:
            place = data['places'][0]  # Take the first result
            formatted_row = [
                location,
                place.get("address", ""),
                place.get("area", ""),
                place.get("city", ""),
                place.get("longitude", ""),
                place.get("latitude", "")
            ]
        else:
            formatted_row = [location, "", "", "", "", ""]  # If no data found, write blank fields

        # Save to CSV
        writer.writerow(formatted_row)
        processed_count += 1

        print(f"✅ Processed {processed_count}: {location} -> {formatted_row}")

        time.sleep(1)  # Avoid hitting rate limits

print(f"✅ Location results saved to {output_file_path}")
print(f"✅ Total locations processed: {processed_count}")
print(f"✅ API responses saved in '{json_output_dir}' directory.")
