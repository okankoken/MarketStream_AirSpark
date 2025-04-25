# airflow/dags/run_spark_consumer.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 20),
}

dag = DAG(
    dag_id='run_spark_consumer',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Spark consumer scriptini calistirir',
)

run_consumer = BashOperator(
    task_id='run_spark_consumer_task',
    bash_command="""
    echo 'Starting Spark Consumer in background...' && \
    docker exec spark_client bash -c 'nohup spark-submit \
        --jars /opt/bitnami/spark/user-jars/spark-sql-kafka-0-10_2.12-3.5.5.jar,\
/opt/bitnami/spark/user-jars/kafka-clients-3.5.1.jar,\
/opt/bitnami/spark/user-jars/spark-token-provider-kafka-0-10_2.12-3.5.5.jar,\
/opt/bitnami/spark/user-jars/commons-pool2-2.11.1.jar,\
/opt/bitnami/spark/user-jars/postgresql-42.7.1.jar,\
/opt/bitnami/spark/user-jars/elasticsearch-spark-30_2.12-8.11.1.jar \
        /opt/spark/scripts/spark_consumer.py > /tmp/consumer.log 2>&1 &' && \
    echo 'Spark Consumer started.'
    """,
    dag=dag
)
