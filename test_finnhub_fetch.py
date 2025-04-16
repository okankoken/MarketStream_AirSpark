# test_finnhub_fetch.py
import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path
import time

# Load API key from .env
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(env_path)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_us_common_stocks(limit=10):
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        symbols = [s["symbol"] for s in response.json() if s.get("type") == "Common Stock"]
        return symbols[:limit]
    else:
        print("Error fetching symbols:", response.text)
        return []

def fetch_full_stock_data(symbol):
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}"
    metric_url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}"

    quote = requests.get(quote_url).json()
    profile = requests.get(profile_url).json()
    metrics = requests.get(metric_url).json()

    if profile.get("country") != "US" or profile.get("name") is None:
        return None  # Sadece US verileri kalsin

    return {
        "symbol": symbol,
        "name": profile.get("name"),  # <-- eklendi
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


def main():
    symbols = get_us_common_stocks()
    print(f"Found {len(symbols)} symbols.")
    for symbol in symbols:
        try:
            data = fetch_full_stock_data(symbol)
            print(json.dumps(data, indent=2))
            time.sleep(1)  # API limit
        except Exception as e:
            print(f"Error with {symbol}:", e)

if __name__ == "__main__":
    main()
