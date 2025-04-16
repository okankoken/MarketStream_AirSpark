from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'finnhub-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Kafka'dan veri dinleniyor...\n")

for message in consumer:
    print(message.value)

