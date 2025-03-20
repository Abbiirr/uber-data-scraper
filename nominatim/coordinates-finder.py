import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import os

# Load the CSV file with unique locations
file_path = "../map/unique_locations.csv"
df_locations = pd.read_csv(file_path)

# Output file
output_file_path = "../extra-csv-files/locations_with_coordinates.csv"

# Initialize geolocator
geolocator = Nominatim(user_agent="location_geocoder")


# Function to get coordinates with retry mechanism
def get_coordinates(location):
    try:
        location_obj = geolocator.geocode(location + ", Dhaka, Bangladesh", timeout=10)
        if location_obj:
            return (location_obj.latitude, location_obj.longitude)
    except GeocoderTimedOut:
        time.sleep(1)
        return get_coordinates(location)
    return (None, None)


# Extract unique locations
unique_locations = df_locations['Unique Locations'].dropna().unique()

# Load existing data if the file exists to avoid reprocessing
if os.path.exists(output_file_path):
    existing_df = pd.read_csv(output_file_path)
    processed_locations = set(existing_df['location'])
else:
    processed_locations = set()

# Open the output CSV in append mode
with open(output_file_path, "a") as f:
    for location in unique_locations:
        if location in processed_locations:
            continue  # Skip locations already processed

        coords = get_coordinates(location)
        if coords != (None, None):
            # Append new data directly to CSV
            f.write(f'"{location}","({coords[0]}, {coords[1]})"\n')
            print(f"Saved: {location} -> {coords}")
        else:
            print(f"Coordinates not found for: {location}")

print(f"Geocoded locations have been saved to {output_file_path}")
