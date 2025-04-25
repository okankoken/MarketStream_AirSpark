#/airflow/scripts/spark_consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
import os
import sys
import shutil

checkpoint_path = "/tmp/spark_multi_checkpoint_airflow"
if os.path.exists(checkpoint_path):
    shutil.rmtree(checkpoint_path)

# PostgreSQL connection
jdbc_url = "jdbc:postgresql://postgres:5432/marketdb"
db_properties = {
    "user": "train",
    "password": "train123",
    "driver": "org.postgresql.Driver"
}

# Spark session
spark = SparkSession.builder \
    .appName("EnrichRealtimeStockData") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Kafka'dan oku
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "realtime-stock-data") \
    .option("startingOffsets", "latest") \
    .load()

# JSON schema
schema = StructType([
    StructField("symbol", StringType()),
    StructField("timestamp", LongType()),
    StructField("price", DoubleType()),
    StructField("high_52week", DoubleType()),
    StructField("low_52week", DoubleType()),
    StructField("volume", DoubleType()),
    StructField("name", StringType()),
    StructField("country", StringType()),
    StructField("exchange", StringType()),
    StructField("finnhubIndustry", StringType()),
    StructField("marketCapitalization", DoubleType()),
    StructField("weburl", StringType()),
    StructField("logo", StringType()),
    StructField("peRatio", DoubleType()),
    StructField("pbRatio", DoubleType()),
    StructField("dividendYield", DoubleType()),
    StructField("beta", DoubleType()),
    StructField("eps", DoubleType()),
    StructField("debtToEquity", DoubleType()),
    StructField("rsi", DoubleType())
])

# JSON'u parse et
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .dropna(subset=["symbol", "price", "timestamp"])

# LOGO olmadan goster
df_display = df_parsed.drop("logo")

# Yalnizca PostgreSQL'e yaz
def write_to_postgres(batch_df, epoch_id):
    if batch_df.isEmpty():
        print("Batch empty, skipping...")
        return

    row_count = batch_df.count()
    print(f"?? Batch received: {row_count} rows ? writing to PostgreSQL...")

    try:
        batch_df.write.jdbc(
            url=jdbc_url,
            table="staging_stocks",
            mode="append",
            properties=db_properties
        )
        print("? Written to PostgreSQL.")
    except Exception as e:
        print("? PostgreSQL write failed:", e)

    batch_df.drop("logo").show(truncate=False)

# Spark Streaming query baslat
query = df_parsed.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_postgres) \
    .option("checkpointLocation", checkpoint_path) \
    .start()

query.awaitTermination()