#/airflow/dags/load_postgres_to_elasticsearch.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from elasticsearch import Elasticsearch, helpers

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'load_postgres_to_elasticsearch',
    default_args=default_args,
    schedule_interval=timedelta(seconds=30),
    catchup=False,
    max_active_runs=1
)

def transfer_data():
    engine = create_engine('postgresql://train:train123@postgres:5432/marketdb')
    df = pd.read_sql("""
        SELECT * FROM realtime_stocks
        WHERE symbol IS NOT NULL
        ORDER BY timestamp DESC
    """, con=engine)

    df = df.drop_duplicates(subset=["symbol"], keep="first")

    es = Elasticsearch("http://elasticsearch:9200")

    # ?? Sadece index yoksa olustur
    if not es.indices.exists(index="stocks_index"):
        es.indices.create(index="stocks_index")

    # ?? Symbol bazli guncelleme
    for _, row in df.iterrows():
        es.index(
            index="stocks_index",
            id=row["symbol"],
            document=row.dropna().to_dict()
        )

    print(f"? Elasticsearch'e {len(df)} kayit overwrite edildi.")



transfer_task = PythonOperator(
    task_id='transfer_postgres_to_es',
    python_callable=transfer_data,
    dag=dag
)