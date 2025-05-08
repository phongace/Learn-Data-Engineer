# producer.py
import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer

# --- Configuration ---
KAFKA_TOPIC = "clickstream_topic"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
USERS = [f"user_{i}" for i in range(1, 6)]  # 5 sample users
URLS = ["/home", "/products", "/products/details/1", "/cart", "/checkout", "/profile"]

# --- Initialize Kafka Producer ---
# value_serializer: a callable that takes a message value and returns a
#                   byte-encoded version of it for transmission to Kafka.
# linger_ms: The producer will wait up to this many milliseconds before sending a batch of messages.
# batch_size: The maximum number of bytes that will be batched.
producer = None
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        linger_ms=10, # Wait up to 10ms to batch messages
        batch_size=16384 # 16KB batch size
    )
    print(f"Kafka Producer connected to {KAFKA_BOOTSTRAP_SERVERS} on topic '{KAFKA_TOPIC}'")
except Exception as e:
    print(f"ERROR: Could not connect to Kafka - {e}")
    print("Please ensure Kafka is running and the bootstrap servers are correct.")
    exit()


def generate_click_event():
    """Generates a sample clickstream event."""
    user_id = random.choice(USERS)
    url = random.choice(URLS)
    timestamp = datetime.now().isoformat(timespec='seconds') # e.g., 2025-05-08T14:30:55
    event = {
        "user_id": user_id,
        "timestamp": timestamp,
        "url": url,
        "event_type": "click"
    }
    return event

if __name__ == "__main__":
    print("Starting Kafka Producer...")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            event_data = generate_click_event()
            producer.send(KAFKA_TOPIC, value=event_data)
            print(f"Sent: {event_data}")
            # Wait for a random interval before sending the next message
            time.sleep(random.uniform(0.5, 2.0))
    except KeyboardInterrupt:
        print("\nProducer stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if producer:
            producer.flush() # Ensure all buffered messages are sent
            producer.close()
            print("Kafka Producer closed.")
