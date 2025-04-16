# finnhub_producer.py
import os
import json
import time
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv("/home/train/dataops/MarketStream_AirSpark/.env")

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
print(FINNHUB_API_KEY)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9094")
print("Kafka broker: ", KAFKA_BROKER)
KAFKA_TOPIC = "realtime-stock-data"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
    retry_backoff_ms=1000,
    request_timeout_ms=30000,
    max_block_ms=60000,
)
# --- Extended Version: More stocks + more metadata ---
def get_all_us_symbols():
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return [stock["symbol"] for stock in response.json() if stock.get("type") == "Common Stock"]
    else:
        print("Error fetching symbol list:", response.text)
        return []

def fetch_profile(symbol):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}"
    return requests.get(url).json()

def fetch_metrics(symbol):
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}"
    return requests.get(url).json()

def fetch_full_stock_data(symbol):
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    quote = requests.get(quote_url).json()
    profile = fetch_profile(symbol)
    metrics = fetch_metrics(symbol)

    return {
        "symbol": symbol,
        "timestamp": int(time.time()),
        "price": quote.get("c"),
        "open": quote.get("o"),
        "high": quote.get("h"),
        "low": quote.get("l"),
        "previous_close": quote.get("pc"),
        "volume": metrics.get("metric", {}).get("volume"),
        "market_cap": profile.get("marketCapitalization"),
        "sector": profile.get("finnhubIndustry"),
        "exchange": profile.get("exchange"),
        "country": profile.get("country"),
        "pe_ratio": metrics.get("metric", {}).get("peNormalizedAnnual"),
        "pb_ratio": metrics.get("metric", {}).get("pbAnnual"),
        "dividend_yield": metrics.get("metric", {}).get("dividendYieldIndicatedAnnual"),
        "52w_high": metrics.get("metric", {}).get("52WeekHigh"),
        "52w_low": metrics.get("metric", {}).get("52WeekLow")
    }

# --- Start full stream loop (?? optionally limited to N stocks for testing) ---
def run_full_producer(limit=None):
    symbols = get_all_us_symbols()
    if limit:
        symbols = symbols[:limit]
    print(f"Producing data for {len(symbols)} symbols...")

    for symbol in symbols:
        try:
            data = fetch_full_stock_data(symbol)
            producer.send(KAFKA_TOPIC, value=data)
            print("Sent:", symbol)
            time.sleep(1)  # prevent rate-limit
        except Exception as e:
            print(f"Error with {symbol}:", str(e))

# ?? TEST AMAcLI AKTIF ET (ilk basta 10 hisseyle dene)
run_full_producer(limit=10)
