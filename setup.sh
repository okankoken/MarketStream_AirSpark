#!/bin/bash

echo "?? Docker start..."
docker compose up -d

echo "? Kafka portu dinleniyor mu diye bakiliyor..."
while ! nc -z localhost 9093; do
  echo "? Kafka portu hala acilmadi..."
  sleep 2
done

echo "?? Kafka icsel olarak da hazir mi diye test ediliyor..."
python3 wait_for_kafka.py

echo "?? Kafka topic'leri olusturuluyor..."
python3 init_topics.py

echo "? Sistem hazir! Producer ve Spark baslatilabilir."
