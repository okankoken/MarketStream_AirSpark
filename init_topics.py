# /home/train/dataops/MarketStream_AirSpark/init_topics.py
import time
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable

broker = "kafka:9092"
topic_name = "realtime-stock-data"

for i in range(10):
    try:
        admin = KafkaAdminClient(bootstrap_servers=broker)
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        admin.create_topics([topic])
        print(f"? Topic created: {topic_name}")
        break
    except TopicAlreadyExistsError:
        print("? Topic already exists.")
        break
    except NoBrokersAvailable:
        print(f"? Broker not ready, retrying... ({i+1}/10)")
        time.sleep(5)
