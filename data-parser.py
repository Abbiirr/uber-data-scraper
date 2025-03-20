import pandas as pd
import os
import json
from datetime import datetime
from kafka import KafkaProducer  # Import Kafka producer

# Kafka configuration
KAFKA_BROKER = "172.16.231.135:31000"
KAFKA_TOPIC = "uber-data-scrap-processed"

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Ensure messages are JSON-encoded
)

# Load data from CSV file
df = pd.read_csv("extra-csv-files/R58T33M77TL_uber_estimates.csv")

# Extract date, time, and datetime
df["date"] = df["Timestamp"].apply(lambda x: x.split()[0])
df["time"] = df["Timestamp"].apply(lambda x: x.split()[1])
df["datetime"] = df["Timestamp"]
df["day_of_week_num"] = df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").weekday())

# Extract fare price using regex
df["fare_price"] = df["Info"].str.extract(r"Fare\s+BDT[\s\xa0]*(\d+\.\d+)").astype(float)

# Extract drop-off time
dropoff_time_df = df["Info"].str.extract(r"estimated drop-off (\d+):(\d+)([ap]m)")
df["dropoff_hour"] = dropoff_time_df[0].astype(float)
df["dropoff_minute"] = dropoff_time_df[1].astype(float)
df["dropoff_period"] = dropoff_time_df[2]

# Extract driver arrival time offset
df["driver_offset"] = df["Info"].str.extract(r"driver is (\d+) minutes away").astype(float).fillna(0)

# Extract travel method
df["method"] = df["Info"].str.extract(r"(Moto Saver|Moto|CNG|UberX)")

# Extract image file name
df["image"] = df["Image Name"].apply(lambda x: os.path.basename(str(x)))

# Convert `time` column into minutes since midnight
df["request_time_minutes"] = df["time"].apply(lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1]))


# Fix drop-off time conversion
def compute_travel_duration(row):
    try:
        if pd.notnull(row["dropoff_hour"]) and pd.notnull(row["dropoff_minute"]) and pd.notnull(row["dropoff_period"]):
            # Convert drop-off time to 24-hour format
            dropoff_hour = int(row["dropoff_hour"])
            dropoff_minute = int(row["dropoff_minute"])
            if row["dropoff_period"] == "pm" and dropoff_hour != 12:
                dropoff_hour += 12
            elif row["dropoff_period"] == "am" and dropoff_hour == 12:
                dropoff_hour = 0

            # Convert drop-off time to minutes since midnight
            dropoff_time_minutes = dropoff_hour * 60 + dropoff_minute

            # Adjust request time by driver offset
            adjusted_request_time = row["request_time_minutes"] + row["driver_offset"]

            # Compute travel duration
            travel_duration = dropoff_time_minutes - adjusted_request_time

            # Ensure travel duration is not negative
            return max(travel_duration, 0)

    except Exception as e:
        print(f"⚠️ Error computing travel duration for row {row.name}: {e}")
    return None


df["travel_duration"] = df.apply(compute_travel_duration, axis=1)

# Extract coordinates
df[["origin_lat", "origin_lon"]] = df["Pickup Coordinates"].str.extract(r"([\d.]+),\s*([\d.]+)").astype(float)
df[["destination_lat", "destination_lon"]] = df["Destination Coordinates"].str.extract(r"([\d.]+),\s*([\d.]+)").astype(
    float)

# Compute travel distance (approximate using Euclidean distance scaled to km)
df["travel_distance_km"] = ((df["destination_lat"] - df["origin_lat"]) ** 2 +
                            (df["destination_lon"] - df["origin_lon"]) ** 2) ** 0.5 * 111

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
final_df.to_csv("parsed_result_new.csv", index=False)

# Display transformed dataset
print(final_df)

# ✅ Publish each row as a JSON message to Kafka
for _, row in final_df.iterrows():
    kafka_message = row.to_dict()
    producer.send(KAFKA_TOPIC, value=kafka_message)
    producer.flush()  # Ensures immediate publishing
    print(f"🚀 Published to Kafka: {kafka_message}")

# Close Kafka producer
producer.close()
