# airflow/dags/realtime_finnhub_dag.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 4, 10),
    "retries": 0,
}

dag = DAG(
    "realtime_finnhub_dag",
    default_args=default_args,
    description="10 saniyede bir finnhub verisi ceken kafka producer DAG",
    schedule_interval=None,  # elle tetiklenecek
    catchup=False,
)

run_looping_script = BashOperator(
    task_id="looping_stock_fetcher",
    bash_command="while true; do python /opt/airflow/dags/finnhub_producer.py; sleep 10; done",
    dag=dag,
)
