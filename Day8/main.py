# main.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# --- Bước 1: Khởi tạo SparkSession với cấu hình JDBC ---
# Thêm .config("spark.jars.packages", ...) để Spark tự tải driver Postgres
# Thay '42.7.3' bằng phiên bản driver bạn muốn, hoặc phiên bản mới hơn nếu cần
print("Đang khởi tạo SparkSession với driver PostgreSQL...")
spark = SparkSession.builder \
    .appName("Ex1_XuLyCSV_to_Postgres") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
    .getOrCreate()

print("SparkSession đã được tạo thành công (với driver Postgres)!")
print("Đối tượng SparkSession:", spark)

# --- Bước 2: Đọc file CSV vào DataFrame (Giữ nguyên) ---
print("\nĐang đọc file SalesData.csv...")
csv_file_path = "SalesData.csv"
df = spark.read.csv(csv_file_path, header=True, inferSchema=True)
print("Đọc file CSV thành công!")
df.show(10)
df.printSchema() # Rất quan trọng để biết cấu trúc cột cần tạo trong DB

# --- Bước 3: Filter (Lọc) dữ liệu (Giữ nguyên) ---
print("\nLọc những dòng có Opportunity Stage = 'Lead':")
lead_opportunities_df = df.filter(col("Opportunity Stage") == "Lead")
print("Hiển thị dữ liệu sau khi lọc theo Opportunity Stage:")
lead_opportunities_df.show(truncate=False)

# --- Bước 4: (Tùy chọn) Lưu DataFrame đã lọc ra CSV (Giữ nguyên nếu bạn vẫn muốn có file CSV) ---
print("\nĐang lưu DataFrame đã lọc (Leads) ra file CSV...")
output_csv_directory = "new_output"
try:
    lead_opportunities_df.coalesce(1).write.csv(output_csv_directory, header=True, mode="overwrite") # Dùng coalesce(1) nếu bạn muốn 1 file CSV
    print(f"Đã lưu dữ liệu Leads thành công vào THƯ MỤC: {output_csv_directory}")
except Exception as e:
    print(f"Lỗi khi lưu file CSV: {e}")

# --- Bước 5: Ghi DataFrame đã lọc vào PostgreSQL ---
print("\nĐang ghi dữ liệu Leads vào PostgreSQL...")

# --- *** THÔNG TIN KẾT NỐI DATABASE - CẦN THAY ĐỔI *** ---
# !!! Cảnh báo Bảo mật: KHÔNG BAO GIỜ hardcode mật khẩu trong code thực tế !!!
# Sử dụng biến môi trường, file config riêng, hoặc vault/secrets manager.
pg_hostname = "localhost"  # Hoặc IP/hostname của server Postgres
pg_port = "5432"         # Cổng mặc định của Postgres
pg_database = "my_database"  # Thay bằng tên DB của bạn
pg_user = "postgres"      # Thay bằng user của bạn
pg_password = "71601998"  # !!! THAY BẰNG PASSWORD CỦA BẠN - Rất không an toàn !!!
pg_table = "sales_leads"  # Đặt tên bảng bạn muốn ghi vào (BẢNG NÀY PHẢI ĐƯỢC TẠO TRƯỚC)

jdbc_url = f"jdbc:postgresql://{pg_hostname}:{pg_port}/{pg_database}"
connection_properties = {
    "user": pg_user,
    "password": pg_password,
    "driver": "org.postgresql.Driver" # Driver class của PostgreSQL
}

try:
    # Ghi DataFrame vào bảng PostgreSQL
    # mode("append"): Nối thêm dữ liệu vào bảng đã có.
    # Các mode khác:
    #  - "overwrite": XÓA SẠCH bảng cũ và tạo lại với dữ liệu mới (CẨN THẬN!).
    #  - "ignore": Nếu bảng tồn tại thì bỏ qua.
    #  - "error" / "errorifexists": Báo lỗi nếu bảng đã tồn tại (mặc định).
    print(f"Chuẩn bị ghi vào bảng '{pg_table}' với mode 'append'...")
    lead_opportunities_df.write.jdbc(
        url=jdbc_url,
        table=pg_table,
        mode="append",  # Chọn "append" để an toàn khi chạy lại
        properties=connection_properties
    )
    print(f"Đã ghi dữ liệu thành công vào bảng PostgreSQL: '{pg_table}'")

except Exception as e:
    # In lỗi chi tiết hơn một chút
    import traceback
    print(f"Lỗi nghiêm trọng khi ghi vào PostgreSQL: {e}")
    print("Traceback:")
    traceback.print_exc()

# --- Bước 6: Dừng Spark Session ---
print("\nĐang dừng SparkSession...")
spark.stop()
print("SparkSession đã dừng.")
