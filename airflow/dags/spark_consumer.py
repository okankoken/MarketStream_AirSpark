#airflow/dags/spark_consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

# PostgreSQL connection info
jdbc_url = "jdbc:postgresql://postgres:5432/marketdb"
db_properties = {
    "user": "train",
    "password": "train123",
    "driver": "org.postgresql.Driver"
}

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

# Yeni JSON schema
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

# JSON'u ayristir
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .dropna(subset=["symbol", "price", "timestamp"])

# LOGO harici kolonlar
columns_to_display = [c for c in df_parsed.columns if c != "logo"]
df_display = df_parsed.select(*columns_to_display)

# Console'a yaz
query = df_display.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()



# ??? PostgreSQL'e yaz
query_postgres = df_parsed.writeStream \
    .outputMode("append") \
    .foreachBatch(lambda batch_df, epoch_id:
        batch_df.write.jdbc(
            url=jdbc_url,
            table="realtime_stocks",
            mode="append",
            properties=db_properties
        )
    ) \
    .option("checkpointLocation", "/tmp/spark_postgres_checkpoint") \
    .start()

query.awaitTermination()


# ? Her iki stream'i de aktif tut
query_console.awaitTermination()
query_postgres.awaitTermination()
