import pandas as pd

# ------------------------------
# Load Grid Boundaries
# ------------------------------
grid_boundaries_path = "grid_boundaries.csv"  # Update path if needed
grid_df = pd.read_csv(grid_boundaries_path)

# ------------------------------
# Load Locations File
# ------------------------------
locations_path = "../filtered_locations.csv"  # Update path if needed
locations_df = pd.read_csv(locations_path, on_bad_lines='skip')  # Skip malformed rows


# ------------------------------
# Extract Latitude & Longitude from Coordinates
# ------------------------------
def parse_coordinates(coord_str):
    """Parses a coordinate string (lat, lon) and returns individual values."""
    try:
        coord_str = coord_str.strip("()")  # Remove parentheses
        lat, lon = map(float, coord_str.split(","))  # Convert to float
        return lat, lon
    except:
        return None, None  # Return None if parsing fails


# Apply coordinate parsing
locations_df[['latitude', 'longitude']] = locations_df['coordinates'].apply(lambda x: pd.Series(parse_coordinates(x)))

# Drop rows where coordinates couldn't be parsed
locations_df = locations_df.dropna(subset=['latitude', 'longitude'])

# Convert to float
locations_df["latitude"] = locations_df["latitude"].astype(float)
locations_df["longitude"] = locations_df["longitude"].astype(float)


# ------------------------------
# Function to Classify Coordinates into Grid Labels
# ------------------------------
def classify_coordinates(lon, lat, grid_df):
    """
    Determines which grid cell a coordinate (longitude, latitude) belongs to.
    Returns the grid label if found, otherwise None.
    """
    matching_grid = grid_df[
        (grid_df["min_x"] <= lon) & (lon <= grid_df["max_x"]) &
        (grid_df["min_y"] <= lat) & (lat <= grid_df["max_y"])
        ]

    if not matching_grid.empty:
        return matching_grid["label"].values[0]  # Return the first matching grid
    return None


# Apply classification
locations_df["grid_label"] = locations_df.apply(
    lambda row: classify_coordinates(row["longitude"], row["latitude"], grid_df), axis=1)

# ------------------------------
# Save the Classified Data
# ------------------------------
output_path = "classified_locations.csv"  # Output file path
locations_df.to_csv(output_path, index=False)

print(f"Classified locations saved to {output_path}")
