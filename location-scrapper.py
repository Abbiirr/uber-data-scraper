import pandas as pd
import requests
import time
import os
import json
import re

# Load CSV file containing locations
file_path = "last_part_quoted_from_pickup_locations.csv"
df_locations = pd.read_csv(file_path)

# Ensure column exists and rename it
if 'Last Part' not in df_locations.columns:
    df_locations.rename(columns={df_locations.columns[0]: 'Last Part'}, inplace=True)

# Barikoi API Key (Replace with your actual key)
API_KEY = "bkoi_4cfa06cfa610e343f92f167449abd92ce859b3629371ea8908b7ffb2fa890721"

# Output CSV file for results
output_file_path = "barikoi_location_results.csv"
json_output_dir = "barikoi_api_responses"

# Ensure the directory for JSON responses exists
os.makedirs(json_output_dir, exist_ok=True)

# Load existing data if the file exists
if os.path.exists(output_file_path):
    existing_df = pd.read_csv(output_file_path)
    processed_locations = set(existing_df['location'].astype(str))
    processed_count = len(existing_df)
else:
    processed_locations = set()
    processed_count = 0


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

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {location}: {e}")

    return None  # Return None if no valid data found


# Open CSV file in append mode
with open(output_file_path, "a", encoding="utf-8") as f:
    for location in df_locations['Last Part'].dropna().astype(str).unique():
        if location in processed_locations:
            continue  # Skip already processed locations

        data = get_barikoi_data(location)

        # Extract relevant fields
        if data and 'places' in data and len(data['places']) > 0:
            place = data['places'][0]  # Take the first result
            formatted_data = f'"{place.get("address", "")}", "{place.get("area", "")}", "{place.get("city", "")}", "{place.get("longitude", "")}", "{place.get("latitude", "")}"'
        else:
            formatted_data = '""'  # If no data found, write blank

        # Save to CSV
        f.write(f'"{location}", {formatted_data}\n')

        processed_count += 1
        print(f"✅ Processed {processed_count}: {location} -> {formatted_data}")

        time.sleep(1)  # Avoid hitting rate limits

print(f"✅ Location results saved to {output_file_path}")
print(f"✅ Total locations processed: {processed_count}")
print(f"✅ API responses saved in '{json_output_dir}' directory.")
