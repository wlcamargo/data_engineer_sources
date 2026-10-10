import json
from kafka import KafkaProducer

TOPIC_NAME = "marketing"
SERVER_ADDRESS = "127.0.0.1:9092"


user_data = {
    "name": "chapolin",
    "address": "brazilandia",
    "email": "chapolin@example.com",
    "country": "brazil"
}

try:
    producer = KafkaProducer(
        bootstrap_servers=SERVER_ADDRESS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: str(k).encode("utf-8"),
    )

    producer.send(TOPIC_NAME, key="leads", value=user_data)
    producer.flush()

    f"Data sent to Kafka topic `{TOPIC_NAME}` with key `leads`!"
    print(user_data)  # Display the sent data
except Exception as e:
    e.error(f"Failed to send message: {e}")