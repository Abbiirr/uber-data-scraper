import pandas as pd
# Load the uploaded file
file_path = "conversation3.txt"

with open(file_path, "r", encoding="utf-8") as file:
    data = file.readlines()

# Process the data to extract relevant information
locations = []

for line in data:
    parts = line.strip().split(",")  # Assuming CSV-like format in the text file
    if len(parts) >= 4:  # Ensuring it has enough data points
        location, area, lat, long = parts[:4]
        try:
            lat = float(lat)
            long = float(long)
            locations.append([location, area, lat, long])
        except ValueError:
            continue  # Skip if lat/long are not valid numbers

# Convert to DataFrame
df = pd.DataFrame(locations, columns=["location", "area", "lat", "long"])

# Save to CSV
output_csv_path = "../extra-csv-files/cleaned_locations-2.csv"
df.to_csv(output_csv_path, index=False)

