# tools/finnhub_realtime_producer.py
import os
import json
import time
import requests
from kafka import KafkaProducer
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

producer = KafkaProducer(
    bootstrap_servers="localhost:9094",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Hisse listesini metadata'dan oku
metadata_df = pd.read_parquet("data/stock_metadata.parquet")
symbols = metadata_df["symbol"].dropna().unique().tolist()

def fetch_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return {
            "symbol": symbol,
            "price": data.get("c"),      # current price
            "timestamp": int(time.time() * 1000)
        }
    return None

def stream_to_kafka():
    print("Streaming started... Press Ctrl+C to stop.")
    while True:
        for sym in symbols[:20]:  # ?? test amacli ilk 20 hisse
            payload = fetch_quote(sym)
            if payload and payload["price"]:
                producer.send("realtime-stock-data", payload)
                print("Sent:", payload)
            time.sleep(0.3)  # API rate limitine takilmamak icin
        time.sleep(5)

if __name__ == "__main__":
    stream_to_kafka()
