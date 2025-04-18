#/airflow/dags/spark_consumer.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

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

# JSON'u ayristir
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .dropna(subset=["symbol", "price", "timestamp"])

# Console icin LOGO'yu cikar
df_display = df_parsed.drop("logo")

# ? Tek bir foreachBatch ile hem PostgreSQL hem Elasticsearch'e yaz
def write_to_postgres_and_elasticsearch(batch_df, epoch_id):
    # PostgreSQL
    batch_df.write.jdbc(
        url=jdbc_url,
        table="staging_stocks",
        mode="append",
        properties=db_properties
    )

    # Elasticsearch
    batch_df.write \
        .format("org.elasticsearch.spark.sql") \
        .option("es.nodes", "elasticsearch") \
        .option("es.port", "9200") \
        .option("es.resource", "stocks_index") \
        .option("es.nodes.wan.only", "true") \
        .mode("append") \
        .save()

    # Console
    batch_df.drop("logo").show(truncate=False)

# writeStream baslat
query = df_parsed.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_postgres_and_elasticsearch) \
    .option("checkpointLocation", "/tmp/spark_multi_checkpoint") \
    .start()

query.awaitTermination()
