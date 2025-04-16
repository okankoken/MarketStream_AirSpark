import pandas as pd
import requests
import json
import time
from kafka import KafkaProducer

API_KEY = "cvtvni1r01qjg136l32gcvtvni1r01qjg136l330"
KAFKA_TOPIC = "realtime-stock-data"

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9094",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


# Symbol listesi
df = pd.read_parquet("data/stock_metadata.parquet")
symbols = df["symbol"].unique().tolist()

# Test icin sadece ilk 10
for symbol in symbols[:10]:
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            quote = res.json()
            quote["symbol"] = symbol
            producer.send(KAFKA_TOPIC, value=quote)
            print(f"Sent to Kafka: {symbol}")
        else:
            print(f"{symbol} error: {res.status_code}")
    except Exception as e:
        print(f"Exception for {symbol}: {e}")
    time.sleep(0.3)  # 60 call per minute = 1 call per ~1s max
