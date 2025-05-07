import json
from kafka import KafkaConsumer

# Cấu hình Kafka Consumer
consumer = KafkaConsumer(
    'sensor-data', # Tên topic cần consume
    bootstrap_servers=['localhost:9092'], # Địa chỉ Kafka broker
    auto_offset_reset='earliest', # Bắt đầu đọc từ message cũ nhất nếu consumer mới
    enable_auto_commit=True, # Tự động commit offset
    group_id='my-sensor-group', # Consumer group ID
    value_deserializer=lambda v: json.loads(v.decode('utf-8')) # Deserializer để chuyển JSON bytes thành dict
)

print("Starting Kafka Consumer...")
print("Listening for messages on topic 'sensor-data'. Press Ctrl+C to stop.")

try:
    for message in consumer:
        # message.value chứa dữ liệu đã được deserialize
        print(f"Received: {message.value}")
        # Bạn có thể thêm logic xử lý dữ liệu ở đây
        # Ví dụ: lưu vào database, hiển thị lên dashboard, v.v.

except KeyboardInterrupt:
    print("Stopping Consumer...")
finally:
    consumer.close()
    print("Consumer closed.")
