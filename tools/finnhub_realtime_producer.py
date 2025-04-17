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

# Top 1000 hisse listesini oku
top_symbols_df = pd.read_parquet("data/stock_metadata_1000.parquet")
symbols = top_symbols_df["symbol"].dropna().unique().tolist()

# Finansal verileri getir

def fetch_combined_data(symbol):
    result = {"symbol": symbol, "timestamp": int(time.time() * 1000)}

    try:
        # Quote verisi (fiyat, hacim, 52 haftalik yuksek/dusuk)
        quote = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}").json()
        result.update({
            "price": quote.get("c"),
            "high_52week": quote.get("h"),
            "low_52week": quote.get("l"),
            "volume": quote.get("v")
        })

        # Company profile (isim, sektor, ulke, logo, site, piyasa degeri)
        profile = requests.get(f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}").json()
        result.update({
            "name": profile.get("name"),
            "country": profile.get("country"),
            "exchange": profile.get("exchange"),
            "finnhubIndustry": profile.get("finnhubIndustry"),
            "marketCapitalization": profile.get("marketCapitalization"),
            "weburl": profile.get("weburl"),
            "logo": profile.get("logo")
        })

        # Temel finansal oranlar (F/K, P/B, borc, beta, EPS, temettu)
        ratios = requests.get(f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}").json()
        metrics = ratios.get("metric", {})
        result.update({
            "peRatio": metrics.get("peBasicExclExtraTTM"),
            "pbRatio": metrics.get("pbAnnual"),
            "dividendYield": metrics.get("dividendYieldIndicatedAnnual"),
            "beta": metrics.get("beta"),
            "eps": metrics.get("epsInclExtraItemsTTM"),
            "debtToEquity": metrics.get("totalDebt/totalEquity")
        })

        # RSI, MACD, hareketli ortalamalar, volatilite
        indicators = requests.get(f"https://finnhub.io/api/v1/indicator?symbol={symbol}&resolution=D&indicator=rsi&token={FINNHUB_API_KEY}").json()
        result["rsi"] = indicators.get("rsi", {}).get("value", [None])[-1] if "rsi" in indicators else None

        # MACD ayri endpoint olmadigindan gosterilmiyor (istege bagli)

    except Exception as e:
        print(f"Hata: {symbol} -> {e}")

    return result

def stream_to_kafka():
    print("Streaming started... Press Ctrl+C to stop.")
    while True:
        for sym in symbols: #[:20]:  # test icin sinirli
            enriched_payload = fetch_combined_data(sym)
            if enriched_payload.get("price"):
                producer.send("realtime-stock-data", enriched_payload)
                print("Sent:\n", json.dumps(enriched_payload, indent=2))  # ?? Tum JSON veriyi goster
            time.sleep(0.5)
        time.sleep(5)

if __name__ == "__main__":
    stream_to_kafka()