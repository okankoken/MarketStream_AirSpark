#fetch_stock_metadata.py
import os
import requests
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  # veya .env dosyasindan da alinabilir

US_EXCHANGES = ["US", "NASDAQ", "NYSE", "AMEX"]

def get_stock_symbols(exchange):
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange={exchange}&token={FINNHUB_API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Error: {exchange} -> {resp.status_code}")
        return []

def collect_all_us_symbols():
    all_data = []
    for ex in US_EXCHANGES:
        print(f"Fetching: {ex}")
        all_data.extend(get_stock_symbols(ex))
    return all_data

def main():
    stock_data = collect_all_us_symbols()
    df = pd.DataFrame(stock_data)
    
    keep_cols = ["symbol", "displaySymbol", "description", "type", "currency", "mic"]
    df = df[keep_cols].drop_duplicates()

    os.makedirs("data", exist_ok=True)
    df.to_parquet("data/stock_metadata.parquet", index=False)
    print(f"Saved to data/stock_metadata.parquet")

if __name__ == "__main__":
    main()
