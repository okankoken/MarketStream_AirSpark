# tools/load_stock_order.py
import pandas as pd
from sqlalchemy import create_engine

# Parquet dosyasini oku
df = pd.read_parquet("/home/train/dataops/MarketStream_AirSpark/data/stock_metadata_1000.parquet")

# Rank ekle (1, 2, 3, ...)
df["rank"] = range(1, len(df) + 1)

# PostgreSQL baglantisi
engine = create_engine("postgresql+psycopg2://train:train123@localhost:5432/marketdb")

# Sadece symbol ve rank kolonlarini al, tabloyu olustur
df[["symbol", "rank"]].to_sql("stock_order", engine, if_exists="replace", index=False)

print("? stock_order tablosu yuklendi.")
