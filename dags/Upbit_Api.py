from datetime import datetime, timedelta
import logging , requests , json

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python_operator import PythonOperator

# created by kimuksung
# 목적 : Upbit bitcoin data collect
# Python -> Call Api -> DB(postgres) 반영 

default_args = {
    'owner': 'kimuksung2',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

def bitcoin_extract(ts):
    time = ts.split('+')[0]
    minute = "1"
    market='KRW-BTC'
    to = time+'Z'
    count = "1"
    url = "https://api.upbit.com/v1/candles/minutes/"+minute+"?market="+market+"&to="+to+"&count="+count
    logging.info(url)
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    json_response = json.loads(response.text)

    return json_response

with DAG(
    dag_id='Upbit_api',
    default_args=default_args,
    start_date=datetime(2022, 7, 19 , 8 , 1 , 00),
    schedule_interval='0 * * * *' #every hour
) as dag:
	# task1 - Create Coin Table
    create_coin_table = PostgresOperator(
        task_id='create_table_coin',
        postgres_conn_id='postgres_xcom_test',
        sql="""
            create table if not exists bitcoin (
                name text,
                time_utc timestamp,
                time_ktc timestamp,
                opening_price double precision,
                high_price double precision,
                low_price double precision,
                trade_price double precision,
                primary key (time_ktc, trade_price)
            )
        """
    )
    # task2 - Call Api Data
    extract_bitcoin = PythonOperator(
        task_id = 'upbit_bitcoin_api_extract',
        python_callable = bitcoin_extract
    )
    # task3 - Coin data Store DB 
    insert_bitcoin = PostgresOperator(
        task_id='insert_bitcoin',
        postgres_conn_id='postgres_xcom_test',
        sql="""
            insert into bitcoin (name , time_utc , time_ktc , opening_price , high_price , low_price , trade_price ) 
            values (
                '{{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['market']}}',
                '{{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['candle_date_time_utc']}}',
                '{{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['candle_date_time_kst']}}',
                {{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['opening_price']}},
                {{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['high_price']}},
                {{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['low_price']}},
                {{task_instance.xcom_pull(task_ids='upbit_bitcoin_api_extract')[0]['trade_price']}}
            )
        """
    )
    create_coin_table >> extract_bitcoin >> insert_bitcoin