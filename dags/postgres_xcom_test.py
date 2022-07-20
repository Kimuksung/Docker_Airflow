from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'kimuksung2',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def get_data():
    return [{'time':'2022-07-18T23:59:00','price':29314000.0}]

with DAG(
    dag_id='postgres_xcom_test',
    default_args=default_args,
    start_date=datetime(2022, 7, 19),
    schedule_interval='0 0 * * *'
) as dag:
    task1 = PostgresOperator(
        task_id='create_postgres_table',
        postgres_conn_id='postgres_xcom_test',
        sql="""
            create table if not exists test_data (
                dt timestamp,
                price double precision
            )
        """
    )
    task2 = PythonOperator(
        task_id='get_data',
        python_callable = get_data
    )
    task3 = PostgresOperator(
        task_id='insert_into_table',
        postgres_conn_id='postgres_xcom_test',
        sql="""
            insert into test_data (dt,price) 
            values ( 
                '{{task_instance.xcom_pull(task_ids='get_data')[0]['time']}}',
                {{task_instance.xcom_pull(task_ids='get_data')[0]['price']}}
            )
        """
    )

    task1 >> task2 >> task3