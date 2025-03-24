import csv
import json
from kafka import KafkaProducer

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers='172.16.231.135:31000',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Path to your CSV
csv_file_path = 'Filtered_Geocoded_Data__Only_Dhaka_.csv'

# Publishing to Kafka
with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        message = {
            "id": row.get("id") or row.get("ID"),
            "original_address": row.get("original_address"),
            "cleaned_address": row.get("cleaned_address"),
            "matched_variation": row.get("matched_variation"),
            "latitude": float(row.get("latitude", 0)),
            "longitude": float(row.get("longitude", 0)),
            "provider": row.get("provider", "Nominatim"),
            "raw_response": json.loads(row.get("raw_response", "{}"))
        }
        print(f"Publishing: {message}")
        producer.send("geocoded_topic", message)

producer.flush()
print("All messages published.")
