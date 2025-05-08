# consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

# --- Configuration ---
KAFKA_TOPIC = "clickstream_topic"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092" # Should match producer's

# --- Define Schema for incoming JSON data ---
# This schema must match the structure of the JSON messages produced by producer.py
click_event_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("timestamp", StringType(), True), # Initially read as String, can be cast to TimestampType later
    StructField("url", StringType(), True),
    StructField("event_type", StringType(), True)
])

if __name__ == "__main__":
    print("Starting Spark Streaming Consumer for Kafka...")

    # --- Initialize SparkSession ---
    # The .config("spark.jars.packages", ...) is crucial for Spark to be able to connect to Kafka.
    # Ensure the version matches your Spark and Scala version.
    # For Spark 3.5.x, org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 is common.
    # Adjust if your Spark/Scala version is different.
    spark = SparkSession.builder \
        .appName("KafkaSparkStreamingClickstream") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN") # Reduce verbosity
    print("SparkSession created.")

    # --- Read from Kafka as a streaming DataFrame ---
    # 'value' column from Kafka is initially binary, needs to be cast to STRING
    raw_kafka_stream_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    print(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")

    # --- Process the stream ---
    # 1. Cast the 'value' (which is binary) to a STRING (assuming UTF-8 JSON)
    # 2. Parse the JSON string using the defined schema
    # 3. Select the fields from the parsed JSON data
    processed_stream_df = raw_kafka_stream_df \
        .selectExpr("CAST(value AS STRING) as json_data") \
        .select(from_json(col("json_data"), click_event_schema).alias("click_event")) \
        .select("click_event.*") \
        .withColumn("timestamp_dt", col("timestamp").cast(TimestampType())) # Optional: cast string timestamp to TimestampType

    # --- Output to console ---
    # OutputMode:
    # "append": Only new rows in the Result Table since the last trigger will be outputted.
    # "complete": The entire updated Result Table will be outputted. (Usually for aggregations)
    # "update": Only the rows that were updated in the Result Table since the last trigger will be outputted.
    query = processed_stream_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    print("Streaming query started. Waiting for data... (Press Ctrl+C to stop)")
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nStreaming query stopped by user.")
    finally:
        print("Shutting down SparkSession.")
        spark.stop()
