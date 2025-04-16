import os
import requests
from dotenv import load_dotenv

# Ortam degiskenlerini yukle
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
STOCK_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

def fetch_stock_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return symbol, response.json()
    else:
        return symbol, f"Error {response.status_code}"

if __name__ == "__main__":
    print("API key used:", FINNHUB_API_KEY)
    for symbol in STOCK_SYMBOLS:
        symbol, data = fetch_stock_quote(symbol)
        print(f"\n=== {symbol} ===")
        print(data)
