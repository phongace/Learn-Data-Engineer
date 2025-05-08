# Apache Spark và Kafka: Xử lý Stream Dữ liệu Clickstream

Dự án này minh họa cách kết hợp Apache Spark Structured Streaming với Apache Kafka để xử lý dòng dữ liệu (stream) theo thời gian thực.
Nó bao gồm:

1.  Một **Kafka Producer** (viết bằng Python) giả lập việc tạo ra dữ liệu clickstream và gửi tới một topic Kafka.
2.  Một **Spark Streaming Consumer** (viết bằng PySpark) đọc dữ liệu từ topic Kafka đó, thực hiện một số biến đổi cơ bản, và hiển thị kết quả ra console.

## 🚀 Kiến trúc Tổng quan

Copy
±----------------+ (JSON Messages) ±--------------------+ (DataFrame) ±------------------+ | Kafka Producer | -------------------------> | Kafka Topic | -------------------> | Spark Streaming | —> Console Output | (producer.py) | (clickstream_topic) | (localhost:9092) | (consumer.py) | | ±----------------+ ±--------------------+ ±------------------+ ^ | (Managed by Docker Compose) | ±--------------------+ | Zookeeper | | (localhost:2181) | ±--------------------+

## 📋 Nội dung Producer và Xử lý của Consumer

### प्रोड्यूसर Kafka (`producer.py`)

- **Nội dung Produce:**
  - Script `producer.py` tạo ra các sự kiện clickstream giả lập dưới dạng message JSON.
  - Mỗi message đại diện cho một hành động "click" của người dùng trên một trang web giả định.
  - Cấu trúc của mỗi message JSON như sau:
    ```json
    {
      "user_id": "user_X", // String: ID của người dùng (ví dụ: "user_1", "user_2", ...)
      "timestamp": "YYYY-MM-DDTHH:MM:SS", // String: Thời gian xảy ra sự kiện (ISO 8601 format)
      "url": "/some_url", // String: URL mà người dùng đã click (ví dụ: "/home", "/products")
      "event_type": "click" // String: Loại sự kiện (luôn là "click" trong ví dụ này)
    }
    ```
  - Dữ liệu được gửi liên tục đến topic Kafka có tên là `clickstream_topic`.

### प्रोसेसर Spark Streaming (`consumer.py`)

- **Nội dung Xử lý:**
  1.  **Kết nối Kafka:** Ứng dụng Spark kết nối với Kafka broker tại `localhost:9092` và đăng ký (subscribe) vào topic `clickstream_topic`.
  2.  **Đọc Dữ liệu Stream:** Dữ liệu được đọc dưới dạng một DataFrame streaming, với mỗi message từ Kafka là một dòng. Cột `value` ban đầu chứa dữ liệu JSON dưới dạng binary.
  3.  **Chuyển đổi và Parse JSON:**
      - Cột `value` (binary) được cast sang kiểu `STRING`.
      - Chuỗi JSON này sau đó được parse dựa trên một schema (`click_event_schema`) đã định nghĩa trước để trích xuất các trường riêng lẻ (`user_id`, `timestamp`, `url`, `event_type`).
  4.  **Thêm cột mới (Tùy chọn):** Một cột mới là `timestamp_dt` được tạo ra bằng cách cast cột `timestamp` (string) sang kiểu `TimestampType` của Spark để dễ dàng thao tác với thời gian hơn nếu cần xử lý sâu hơn.
  5.  **Hiển thị Output:** DataFrame đã xử lý được hiển thị ra console ở chế độ `append` (chỉ hiển thị các dòng mới trong mỗi micro-batch). Kết quả bao gồm các trường đã parse và cột `timestamp_dt` mới.

## ⚙️ Yêu cầu Hệ thống

- **Python 3.x**
- **Pip** (Python package installer)
- **Docker** và **Docker Compose** (để chạy Kafka và Zookeeper)
- **Java Development Kit (JDK)** (thường là phiên bản 8 hoặc 11, cần cho Spark)

## 🛠️ Hướng dẫn Cài đặt và Chạy

1.  **Clone Repository (Nếu có):**

    ```bash
    # git clone <your-repo-url>
    # cd <your-repo-directory>
    ```

2.  **Cài đặt thư viện Python cần thiết:**
    Mở terminal và chạy:

    ```bash
    pip3 install pyspark kafka-python
    ```

    - `pyspark`: Thư viện Apache Spark cho Python.
    - `kafka-python`: Thư viện client Kafka cho Python (dùng bởi `producer.py`).

3.  **Khởi chạy Kafka và Zookeeper bằng Docker Compose:**
    Đảm bảo Docker Desktop đang chạy. Trong thư mục gốc của dự án (chứa file `docker-compose.yml`), chạy:

    ```bash
    docker-compose up -d
    ```

    Lệnh này sẽ tải images (nếu chưa có) và khởi chạy Zookeeper và Kafka trong các container ở chế độ nền.

    - Zookeeper sẽ chạy trên port `2181`.
    - Kafka broker sẽ chạy trên port `9092` (cho client bên ngoài) và `29092` (cho giao tiếp nội bộ).

4.  **Chạy Kafka Producer:**
    Mở một **Terminal MỚI** (Tab 1). `cd` vào thư mục dự án và chạy:

    ```bash
    python3 producer.py
    ```

    Bạn sẽ thấy các message JSON được gửi đi, ví dụ:

    ```
    Kafka Producer connected to localhost:9092 on topic 'clickstream_topic'
    Starting Kafka Producer...
    Press Ctrl+C to stop.
    Sent: {'user_id': 'user_3', 'timestamp': '2025-05-08T16:20:11', 'url': '/profile', 'event_type': 'click'}
    Sent: {'user_id': 'user_1', 'timestamp': '2025-05-08T16:20:12', 'url': '/cart', 'event_type': 'click'}
    ```

    **Để nguyên Terminal này chạy.**

5.  **Chạy Spark Streaming Consumer:**
    Mở một **Terminal MỚI khác** (Tab 2). `cd` vào thư mục dự án và chạy:

    ```bash
    python3 consumer.py
    ```

    _Lưu ý: Lần đầu chạy, Spark có thể mất một chút thời gian để tải các package cần thiết (ví dụ: `spark-sql-kafka-0-10`)._
    Sau khi Spark khởi động và kết nối, bạn sẽ thấy output dạng bảng được cập nhật liên tục với dữ liệu từ Kafka:

    ```
    SparkSession created.
    Subscribed to Kafka topic: clickstream_topic
    Streaming query started. Waiting for data... (Press Ctrl+C to stop)
    -------------------------------------------
    Batch: 0
    -------------------------------------------
    +-------+-------------------+---------------------+----------+-------------------+
    |user_id|timestamp          |url                  |event_type|timestamp_dt       |
    +-------+-------------------+---------------------+----------+-------------------+
    |user_3 |2025-05-08T16:20:11|/profile             |click     |2025-05-08 16:20:11|
    |user_1 |2025-05-08T16:20:12|/cart                |click     |2025-05-08 16:20:12|
    +-------+-------------------+---------------------+----------+-------------------+
    ... (các batch mới sẽ xuất hiện)
    ```

6.  **Dọn dẹp:**
    - Để dừng producer: Nhấn `Ctrl+C` trong Terminal của `producer.py`.
    - Để dừng consumer: Nhấn `Ctrl+C` trong Terminal của `consumer.py`.
    - Để dừng và xóa các container Kafka/Zookeeper:
      ```bash
      docker-compose down
      ```

## 💡 Điểm cần Lưu ý

- **Phiên bản Kafka Connector cho Spark:** File `consumer.py` sử dụng `.config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")`. Hãy đảm bảo phiên bản này (`3.5.0`) tương thích với phiên bản Spark bạn đang sử dụng. Điều chỉnh nếu cần.
- **Cấu hình Kafka:** Các script đang sử dụng `localhost:9092` làm địa chỉ Kafka bootstrap server. Nếu Kafka của bạn chạy ở địa chỉ khác, hãy cập nhật trong cả `producer.py` và `consumer.py`.
- **Xử lý lỗi và Mở rộng:** Đây là một ví dụ cơ bản. Trong thực tế, bạn sẽ cần thêm các cơ chế xử lý lỗi, checkpointing cho Spark Streaming, và các logic xử lý dữ liệu phức tạp hơn.
