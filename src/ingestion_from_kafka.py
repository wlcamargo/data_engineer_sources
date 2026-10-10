import json

from kafka import KafkaConsumer
from datetime import datetime
import os

from functions.s3_utils import upload_to_s3 

TOPIC_NAME = "marketing"
SERVER_ADDRESS = "127.0.0.1:9092"


def safe_deserializer(v):
    """Safely deserialize JSON data, handling empty or invalid messages."""
    if not v:
        return None
    try:
        return json.loads(v.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Warning: Failed to deserialize message: {e}")
        return None


def consume_and_store():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=SERVER_ADDRESS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="consumer-group-leads",
        value_deserializer=safe_deserializer,
        key_deserializer=lambda k: k.decode("utf-8") if k else None
    )

    print(f"Listening for messages on topic `{TOPIC_NAME}`...")

    for message in consumer:
        # Skip messages with no value or failed deserialization
        if message.value is None:
            print("Skipping empty or invalid message")
            continue
            
        key = message.key or "nokey"
        value = message.value

        filename = f"{key}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.json"

        data_json = json.dumps(value)

        upload_to_s3(filename, data_json, source="kafka")

        print(f"Saved message to MinIO bucket as {filename}")

if __name__ == "__main__":
    consume_and_store()