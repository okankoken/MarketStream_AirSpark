from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, LongType
import os

# Spark session
spark = SparkSession.builder \
    .appName("EnrichRealtimeStockData") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Kafka'dan veri oku
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "realtime-stock-data") \
    .option("startingOffsets", "latest") \
    .load()

# JSON semasi
schema = StructType() \
    .add("symbol", StringType()) \
    .add("price", DoubleType()) \
    .add("timestamp", LongType())

# JSON'u parse et
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .dropna(subset=["symbol", "price", "timestamp"])

# Metadata dosyasi yolu (mutlaka container icindeki mount path)
metadata_path = "/opt/bitnami/spark/data/stock_metadata.parquet"

# metadata dosyasini sadece varsa oku
if os.path.exists(metadata_path):
    metadata_df = spark.read.parquet(metadata_path) \
        .dropna(subset=["symbol"]) \
        .dropDuplicates(["symbol"])
else:
    # Bos bir DataFrame yarat (sema uyusmali)
    metadata_df = spark.createDataFrame([], schema=StructType().add("symbol", StringType()) \
                                                           .add("displaySymbol", StringType()) \
                                                           .add("description", StringType()) \
                                                           .add("type", StringType()) \
                                                           .add("currency", StringType()) \
                                                           .add("mic", StringType()))

# join ile enrich
df_enriched = df_parsed.join(metadata_df, on="symbol", how="left")

# ciktiyi yaz
query = df_enriched.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
