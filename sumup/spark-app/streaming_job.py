from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, TimestampType

spark = SparkSession.builder.appName("SpotifyStreaming").getOrCreate()

schema = StructType() \
    .add("user_id", StringType()) \
    .add("track_id", StringType()) \
    .add("timestamp", TimestampType())

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "user_events") \
    .option("startingOffsets", "earliest") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

query = json_df.writeStream.format("console").start()

query.awaitTermination()
