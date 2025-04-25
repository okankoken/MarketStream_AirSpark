from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, FloatType, LongType
import os

# ?? Elasticsearch ayarlari
es_host = "http://elasticsearch:9200"
es_index = "realtime_stock_data"

# ?? PostgreSQL ayarlari
pg_url = "jdbc:postgresql://postgres:5432/marketdb"
pg_properties = {
    "user": "train",
    "password": "train123",
    "driver": "org.postgresql.Driver"
}

# ?? Kafka topic
kafka_topic = "realtime_stock_data"

# ?? JSON yapisi (finnhub_producer.py ile ayni olmali)
schema = StructType() \
    .add("symbol", StringType()) \
    .add("price", FloatType()) \
    .add("volume", LongType()) \
    .add("timestamp", LongType())

# ?? SparkSession
spark = SparkSession.builder \
    .appName("RealtimeStockStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.2.27") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ?? Kafka'dan veri oku
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "latest") \
    .load()

# ?? Kafka 'value' alani JSON olarak parse et
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# ? Elasticsearch'e yaz
df_parsed.writeStream \
    .outputMode("append") \
    .format("org.elasticsearch.spark.sql") \
    .option("checkpointLocation", "/tmp/spark-checkpoint-elastic") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("es.resource", es_index) \
    .start()

# ? PostgreSQL'e yaz
df_parsed.writeStream \
    .foreachBatch(lambda df, epochId: df.write.jdbc(pg_url, "realtime_stock_data", mode="append", properties=pg_properties)) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/spark-checkpoint-postgres") \
    .start() \
    .awaitTermination()
