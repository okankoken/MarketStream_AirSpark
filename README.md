
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
