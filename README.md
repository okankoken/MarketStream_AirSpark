# 📈 MarketStream_AirSpark

Gerçek zamanlı ABD hisse senedi verilerini toplayan, zenginleştiren ve analiz eden bir veri mühendisliği projesidir. Veriler Finnhub API üzerinden çekilir, Apache Kafka ile iletilir, Apache Spark ile işlenir ve zenginleştirilir.

## 🚀 Kullanılan Teknolojiler

- 📨 **Kafka** — Gerçek zamanlı veri kuyruğu
- ⚡ **Apache Spark** — Streaming veriyi işleme
- 🧪 **Finnhub API** — Anlık ve geçmiş finansal veriler
- 🐍 **Python** — Producer & veri işleme
- 🐘 **PostgreSQL** (İleride)
- 📊 **Kibana / Power BI** (İleride görselleştirme için)
- 🐳 **Docker Compose** — Tüm servisleri ayağa kaldırmak için

---

## 📁 Proje Dizini

```
MarketStream_AirSpark/
├── airflow/
│   └── dags/
│       ├── finnhub_realtime_producer.py   # API verilerini Kafka'ya yollar
│       └── spark_consumer.py              # Spark ile Kafka'dan veri çeker
├── data/
│   ├── stock_metadata_1000.parquet        # İlk 1000 hissenin temel bilgileri
├── tools/
│   └── fetch_stock_metadata.py            # Hisse metadata'larını indirip kaydeder
├── .env                                   # API anahtarı burada
├── docker-compose.yml                     # Tüm servisler buradan başlatılır
```

---

## ⚙️ Kurulum

### 1. Ortam Değişkenleri

Proje kök dizininde bir `.env` dosyası oluştur:

```env
FINNHUB_API_KEY=senin_finnhub_api_keyin
```

---

### 2. Docker Servislerini Başlat

```bash
docker compose up -d --build
```

---

### 3. İlk 1000 Hisseyi Belirle (İsteğe bağlı)

```bash
python tools/fetch_stock_metadata.py
```

Bu script çalıştığında `data/stock_metadata_1000.parquet` dosyasını üretir.

---

## 🚀 Akış Özeti
1. `finnhub_realtime_producer.py` → API'den veri çek, Kafka'ya gönder (`localhost:9094`)
2. `spark_consumer.py` → Kafka'dan oku, metadata ile birleştir, console'a yaz


## 🔁 Veri Akışı

### 1. Kafka Producer'ı Başlat

Aşağıdaki script Finnhub API'den zenginleştirilmiş verileri çekip Kafka’ya yollar:

```bash
cd airflow/dags/
python finnhub_realtime_producer.py
```

⏺ Gönderilen veri şunları içerir:
- Fiyat, Hacim, 52 haftalık yüksek/düşük
- Şirket adı, sektör, ülke, borsa
- Piyasa değeri, F/K, P/B, temettü, beta, EPS
- RSI gibi teknik göstergeler

---

### 2. Spark Consumer'ı Çalıştır

Kafka'dan gelen verileri okuyup işlemek için Spark container içinde şu komutu çalıştır:

```bash
docker exec -it spark_client spark-submit \
  --jars /opt/bitnami/spark/user-jars/spark-sql-kafka-0-10_2.12-3.5.5.jar,\
/opt/bitnami/spark/user-jars/kafka-clients-3.5.1.jar,\
/opt/bitnami/spark/user-jars/spark-token-provider-kafka-0-10_2.12-3.5.5.jar,\
/opt/bitnami/spark/user-jars/commons-pool2-2.11.1.jar,\
/opt/bitnami/spark/user-jars/postgresql-42.7.1.jar \
  /opt/airflow/dags/spark_consumer.py
```

💡 `logo` (firma logosu) sütunu konsolda görüntülenmez ama veri olarak tutulur.

---

## Kafka'da Gerçek Zamanlı Mesajları Görmek İçin:

```commandline
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic realtime-stock-data \
  --from-beginning
```


## ✅ Örnek Kafka Verisi

```json
{
  "symbol": "AAPL",
  "timestamp": 1744926599160,
  "price": 196.98,
  "high_52week": 198.8335,
  "low_52week": 194.42,
  "volume": null,
  "name": "Apple Inc",
  "country": "US",
  "exchange": "NASDAQ NMS - GLOBAL MARKET",
  "finnhubIndustry": "Technology",
  "marketCapitalization": 2918338.16,
  "weburl": "https://www.apple.com/",
  "peRatio": 30.21,
  "pbRatio": 61.84,
  "dividendYield": 0.51,
  "beta": 1.29,
  "eps": 6.29,
  "debtToEquity": null,
  "rsi": null
}
```

---

## 📌 Notlar

- Kafka Topic: `realtime-stock-data`
- Spark batch çıktıları düzenli aralıklarla terminale yazılır.
- `stock_metadata_1000.parquet` sadece ilk 1000 önemli hisseyi içerir.
---




