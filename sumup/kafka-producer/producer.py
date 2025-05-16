from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(bootstrap_servers='kafka-1:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

events = [
    {"user_id": "1", "track_id": "track_1", "timestamp": "2025-05-15T12:00:00Z"},
    {"user_id": "2", "track_id": "track_2", "timestamp": "2025-05-15T12:01:00Z"},
    # thêm event khác...
]

while True:
    for e in events:
        producer.send('user_events', e)
        print(f"Sent event: {e}")
        time.sleep(5)
