
```
Adım	Açıklama
🏁 1	Proje klasörü ve venv oluşturuldu.
⚙️ 2	docker-compose.yml ile Kafka, PostgreSQL, Elasticsearch, Kibana kuruldu.
🚦 3	Airflow kurulumu tamamlandı (init, webserver, scheduler)
🧠 4	finnhub_producer.py ile veri üretici script yazıldı
🌐 5	DAG (realtime_finnhub_dag.py) yazıldı ve UI'de çalıştı.
🔁 6	GitHub senkronizasyonu sağlandı (git-sync ✅)
```

```
🎯 Projenin Amacı:
"Amerika borsalarındaki (NASDAQ, NYSE, DOW JONES) hisse senetlerinin gerçek zamanlı verilerini Kafka üzerinden toplayıp, Apache Spark ile işleyerek PostgreSQL ve Elasticsearch'e yazmak. Ardından bu verileri Airflow ile otomatikleştirip, Power BI ve Kibana üzerinden canlı analiz ve görselleştirme yapmak."

🔍 Hedeflenen Çıktılar:
Gerçek zamanlı hisse verisi toplama (price, volume, timestamp vs.)

Kafka ile akış yönetimi

Spark ile veri işleme ve filtreleme

PostgreSQL: analiz için veritabanına yazım

Elasticsearch: Kibana dashboard için

Power BI: dış kullanıcıya görsel raporlar

Airflow: tüm bu süreci DAG ile otomatikleştirme

```


### Gerekli Spark Kafka JAR’ları

Bu proje aşağıdaki JAR'lara ihtiyaç duyar:
- spark-sql-kafka-0-10_2.12-3.5.5.jar
- kafka-clients-3.5.1.jar
- spark-token-provider-kafka-0-10_2.12-3.5.5.jar
- commons-pool2-2.11.1.jar

Lütfen bu dosyaları `./jars` dizinine indirip mount ettiğinizden emin olun.



---

```
MarketStream_AirSpark/
│
├── tools/
│   └── finnhub_realtime_producer.py   # API -> Kafka stream
│
├── airflow/dags/
│   └── spark_consumer.py              # Kafka -> Spark -> Console (enrich)
│
├── data/
│   └── stock_metadata.parquet         # Symbol metadata cache
│
├── jars/                              # Spark Kafka JAR’ları
│   └── *.jar

```

# 📈 MarketStream_AirSpark: Realtime Stock Stream

## 🚀 Akış Özeti
1. `finnhub_realtime_producer.py` → API'den veri çek, Kafka'ya gönder (`localhost:9094`)
2. `spark_consumer.py` → Kafka'dan oku, metadata ile birleştir, console'a yaz

## 🔹 Metadata Hazırla
```bash
python tools/fetch_stock_metadata.py
# → data/stock_metadata.parquet oluşur
```

## 🔹 Kafka Producer (Canlı Veri Gönderimi)
```bash
python tools/finnhub_realtime_producer.py
# İlk 20 hisse, Kafka topic: realtime-stock-data
```

## 🔹 Spark Consumer (Veriyi Console'a Bas)
```bash
docker exec -it spark_client spark-submit \
  --jars /opt/bitnami/spark/user-jars/spark-sql-kafka-0-10_2.12-3.5.5.jar,\
/opt/bitnami/spark/user-jars/kafka-clients-3.5.1.jar,\
/opt/bitnami/spark/user-jars/spark-token-provider-kafka-0-10_2.12-3.5.5.jar,\
/opt/bitnami/spark/user-jars/commons-pool2-2.11.1.jar \
  /opt/airflow/dags/spark_consumer.py
```

## 🔹 Test için Kafka’ya Manuel Veri Gönder
```bash
echo '{"symbol": "AAPL", "price": 192.31, "timestamp": 1713893600000}' | \
docker exec -i kafka kafka-console-producer.sh \
--broker-list localhost:9092 --topic realtime-stock-data
```

## ✅ Notlar
- `metadata.parquet` Spark container’da `/opt/bitnami/spark/data/` içine mount edildi
- Spark Kafka `.jar`'ları `--jars` ile eklenmeli
- Console’da batch olarak enriched veri görünür



