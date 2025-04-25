# airflow/dags/run_finnhub_producer.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 18),
}

dag = DAG(
    dag_id='run_finnhub_producer',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Finnhub real-time producer scriptini calistirir',
)

run_producer = BashOperator(
    task_id='run_finnhub_producer_task',
    bash_command="""
        echo 'Starting producer in background...' && \
        docker exec spark_client bash -c 'nohup python3 /opt/spark/scripts/finnhub_realtime_producer.py > /tmp/producer.log 2>&1 &' && \
        echo 'Producer started.'
    """,
    dag=dag,
)
