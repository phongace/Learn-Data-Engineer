# main.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Bước 1: Khởi tạo SparkSession
# Đảm bảo các dòng .appName, .master, .getOrCreate thẳng hàng với nhau
# và thụt vào so với dòng spark = ...
spark = SparkSession.builder \
    .appName("Ex1_XuLyCSV") \
    .master("local[*]") \
    .getOrCreate()  # Kiểm tra kỹ dòng này, không có space/tab thừa ở đầu

print("SparkSession đã được tạo thành công!")
print("Đối tượng SparkSession:", spark)

# --- Bước 2: Đọc file CSV vào DataFrame ---
print("\nĐang đọc file SalesData.csv...")
# Đường dẫn tới file CSV của bạn (ở đây là cùng thư mục nên chỉ cần tên file)
csv_file_path = "SalesData.csv"

# Sử dụng spark.read.csv để đọc file
# header=True: Dòng đầu tiên là header (tên cột)
# inferSchema=True: Spark tự động suy luận kiểu dữ liệu cho các cột
# Bạn có thể thay đổi các tùy chọn này nếu cần
df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

# Kiểm tra xem DataFrame đã được đọc đúng chưa
print("Đọc file CSV thành công!")
print("Hiển thị 10 dòng đầu tiên của dữ liệu:")
df.show(10) # show() dùng để hiển thị dữ liệu

print("Hiển thị cấu trúc (schema) của DataFrame:")
df.printSchema() # printSchema() dùng để xem tên cột và kiểu dữ liệu

print("\nLọc những dòng có Opportunity Stage = 'Lead':")

# Sử dụng col() để tham chiếu cột và toán tử == để so sánh bằng
# Chú ý là dùng hai dấu bằng (==) để so sánh nhé!
lead_opportunities_df = df.filter(col("Opportunity Stage") == "Lead")

# lead_opportunities_df là DataFrame mới chỉ chứa các dòng thỏa mãn điều kiện
print("Hiển thị dữ liệu sau khi lọc theo Opportunity Stage:")
lead_opportunities_df.show(truncate=False)
