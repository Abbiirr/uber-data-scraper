import pandas as pd
from kafka import KafkaProducer
import json

# Load the CSV
df = pd.read_csv("filtered_trip_locations_in_dhaka.csv")

# Show row count
print(f"📦 Total rows to publish: {len(df)}")

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='172.16.231.135:31000',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Iterate and publish to Kafka
for idx, row in df.iterrows():
    message = {
        "id": idx,
        "address": row["location"]
    }
    print(f"🚀 Publishing: {message}")
    producer.send("address_topic", value=message)

producer.flush()
print("✅ Done publishing all rows to 'address_topic'")
