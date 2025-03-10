import pandas as pd
from datetime import datetime
import os

# Load data from CSV file
df = pd.read_csv("b7da0983_uber_estimates.csv")

# Extract date, time, and datetime
df["date"] = df["Timestamp"].apply(lambda x: x.split()[0])
df["time"] = df["Timestamp"].apply(lambda x: x.split()[1])
df["datetime"] = df["Timestamp"]
df["day_of_week_num"] = df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").weekday())

# Extract fare price with better regex to handle different whitespace characters
df["fare_price"] = df["Info"].str.extract(r"Fare\s+BDT[\s\xa0]*(\d+\.\d+)").astype(float)

# Extract drop-off time
dropoff_time_df = df["Info"].str.extract(r"estimated drop-off (\d+):(\d+)([ap]m)")
df["dropoff_hour"] = dropoff_time_df[0].astype(float)
df["dropoff_minute"] = dropoff_time_df[1].astype(float)
df["dropoff_period"] = dropoff_time_df[2]

# Extract driver arrival time offset
df["driver_offset"] = df["Info"].str.extract(r"driver is (\d+) minutes away").astype(float).fillna(0)

# Extract travel method, considering cases where method appears later in the Info string
df["method"] = df["Info"].str.extract(r"(Moto Saver|Moto|CNG|UberX)")

# Extract image file name without folder path
df["image"] = df["Image Name"].apply(lambda x: os.path.basename(str(x)))


# Compute travel duration
def compute_travel_duration(hour, minute, period, driver_offset):
    if pd.notnull(hour) and pd.notnull(minute) and pd.notnull(period):
        hour = int(hour)
        minute = int(minute)
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0

        # Adjust start time by driver offset
        start_hour, start_minute = 14, 59  # Initial ride request time
        adjusted_start = (start_hour * 60 + start_minute) + driver_offset
        return (hour * 60 + minute) - adjusted_start
    return None


df["travel_duration"] = df.apply(
    lambda row: compute_travel_duration(row["dropoff_hour"], row["dropoff_minute"], row["dropoff_period"],
                                        row["driver_offset"]), axis=1)

# Extract coordinates
df[["origin_lat", "origin_lon"]] = df["Pickup Coordinates"].str.extract(r"([\d.]+),\s*([\d.]+)").astype(float)
df[["destination_lat", "destination_lon"]] = df["Destination Coordinates"].str.extract(r"([\d.]+),\s*([\d.]+)").astype(
    float)

# Compute travel distance (approximate using Euclidean distance scaled to km)
df["travel_distance_km"] = ((df["destination_lat"] - df["origin_lat"]) ** 2 + (
            df["destination_lon"] - df["origin_lon"]) ** 2) ** 0.5 * 111

# Rename columns to match expected output
df.rename(columns={
    "Start Location Name": "origin_name",
    "End Location Name": "destination_name"
}, inplace=True)

# Select required columns
final_df = df[
    ["origin_name", "origin_lon", "origin_lat", "destination_name", "destination_lon", "destination_lat", "date",
     "time", "datetime", "fare_price", "travel_duration", "day_of_week_num", "travel_distance_km", "method", "image"]]

# Save transformed dataset to CSV
final_df.to_csv("parsed_result.csv", index=False)

# Display transformed dataset
print(final_df)