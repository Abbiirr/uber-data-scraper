import pandas as pd
import unicodedata
import re

# Standardization function
def standardize_text(text):
    text = str(text).strip().lower()
    # Normalize accented characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Remove all double quotes
    text = text.replace('"', '')
    # Remove extra spaces around commas so that "Sector 4, Uttara" and "Sector 4,uttara" become the same
    text = re.sub(r'\s*,\s*', ',', text)
    # Normalize remaining spaces
    text = re.sub(r'\s+', ' ', text)
    return text

# Load the processed locations CSV (reference)
# (This file contains two columns: location and area)
processed_df = pd.read_csv("../processed locations/Processed_Locations.csv", header=0)
# Standardize the 'location' column in the processed data
processed_df["std_location"] = processed_df["location"].apply(standardize_text)

# Load the unique pickup points CSV (all locations)
unique_df = pd.read_csv("../extra-csv-files/unique_pickup_points.csv", header=0)
# Assume the column is named "Location Name" or "location" – adjust if needed.
if "Location Name" in unique_df.columns:
    unique_df.rename(columns={"Location Name": "location"}, inplace=True)
unique_df["std_location"] = unique_df["location"].apply(standardize_text)

# Create a set of standardized processed locations for fast lookup
processed_set = set(processed_df["std_location"])

# Identify matched locations from unique pickup points (those that appear in processed locations)
matched_df = unique_df[unique_df["std_location"].isin(processed_set)].copy()
remaining_df = unique_df[~unique_df["std_location"].isin(processed_set)].copy()

# Optionally, drop the standardized columns before export
matched_df = matched_df.drop(columns=["std_location"])
remaining_df = remaining_df.drop(columns=["std_location"])

# Save the results to CSV files
matched_csv_path = "../extra-csv-files/Matched_Locations.csv"
remaining_csv_path = "../extra-csv-files/Remaining_Locations.csv"
matched_df.to_csv(matched_csv_path, index=False)
remaining_df.to_csv(remaining_csv_path, index=False)

# Print counts
print("Matched locations count:", len(matched_df))
print("Remaining locations count:", len(remaining_df))
