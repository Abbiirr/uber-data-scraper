import json
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, BigInteger, String, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------
# PostgreSQL Configuration
# -----------------------
DATABASE_URL = 'postgresql://zalando:6X9VdTow59UbSPvCD70RD0w98mviGScgFEfnHX2LyCZkfAzPRZyMS51CzznNTKzr@172.16.231.135:31704/gigly'

engine = create_engine(DATABASE_URL)
Base = declarative_base()


class ClassifiedLocation(Base):
    __tablename__ = 'classified_locations'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    original_address = Column(Text)
    cleaned_address = Column(Text)
    matched_variation = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    provider = Column(String(100))
    area = Column(String(100))  # ✅ Added field
    raw_response = Column(JSON)


# Create table if it doesn't exist
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# -----------------------
# Kafka Consumer Setup
# -----------------------
consumer = KafkaConsumer(
    'classified_location_success',
    bootstrap_servers='172.16.231.135:31000',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='classified-location-db-writer',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🚀 Listening to 'classified_location_success'...")

for message in consumer:
    data = message.value
    print(f"📥 Received: {data}")

    try:
        data.pop('id', None)  # ensure 'id' doesn't conflict with serial
        record = ClassifiedLocation(
            original_address=data.get('original_address'),
            cleaned_address=data.get('cleaned_address'),
            matched_variation=data.get('fixed_variation'),
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0)),
            provider=data.get('provider'),
            area=data.get('classified_area'),  # ✅ Set area from Kafka message
            raw_response=data.get('raw_response', {})  # ✅ Use dict directly
        )

        session.add(record)
        session.commit()
        print("✅ Saved to DB.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving record: {e}")
