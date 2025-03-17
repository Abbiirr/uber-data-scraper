from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import pandas as pd

# Load the newly uploaded CSV file with unique locations
file_path = "cleaned_unique_locations.csv"
df_locations = pd.read_csv(file_path)

# Initialize geolocator
geolocator = Nominatim(user_agent="location_geocoder")

# Function to get coordinates with retry mechanism
def get_coordinates(location):
    try:
        location_data = geolocator.geocode(location + ", Dhaka, Bangladesh", timeout=10)
        if location_data:
            return (location_data.latitude, location_data.longitude)
    except GeocoderTimedOut:
        time.sleep(1)
        return get_coordinates(location)
    return (None, None)

# Extract unique locations
unique_locations = df_locations['Location'].unique()

# Create a dictionary to store location coordinates
location_coords = {}

# Geocode each unique location
for location in unique_locations:
    coords = get_coordinates(location)
    if coords != (None, None):
        location_coords[location] = coords
    else:
        print(f"Coordinates not found for: {location}")

# Create a new DataFrame with coordinates
formatted_data = []
for location, coords in location_coords.items():
    formatted_data.append({
        'Location': location,
        'Coordinates': f'"({coords[0]}, {coords[1]})"'
    })

# Convert to DataFrame
formatted_df = pd.DataFrame(formatted_data)

# Save to CSV
output_file_path = "unique_locations_with_coordinates.csv"
formatted_df.to_csv(output_file_path, index=False)

# Provide the file for download
output_file_path
