import time
import json
import random
from kafka import KafkaProducer

# Cấu hình Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'], # Địa chỉ Kafka broker
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # Serializer để chuyển dict thành JSON bytes
)

# Tên topic Kafka
TOPIC_NAME = 'sensor-data'

def generate_sensor_data():
    """Tạo dữ liệu sensor ngẫu nhiên."""
    return {
        'sensor_id': f'sensor_{random.randint(1, 10)}',
        'timestamp': time.time(),
        'temperature': round(random.uniform(15.0, 30.0), 2),
        'humidity': round(random.uniform(40.0, 70.0), 2),
        'pressure': round(random.uniform(980.0, 1020.0), 2)
    }

print("Starting Kafka Producer...")
print(f"Sending messages to topic: {TOPIC_NAME}")
print("Press Ctrl+C to stop.")

try:
    while True:
        data = generate_sensor_data()
        # Gửi message đến topic
        producer.send(TOPIC_NAME, value=data)
        print(f"Sent: {data}")
        # Đợi một khoảng thời gian ngẫu nhiên để mô phỏng việc gửi sự kiện thời gian thực
        time.sleep(random.uniform(0.5, 2.0))
except KeyboardInterrupt:
    print("Stopping Producer...")
finally:
    producer.flush() # Đảm bảo tất cả các message đã được gửi trước khi đóng
    producer.close()
    print("Producer closed.")
