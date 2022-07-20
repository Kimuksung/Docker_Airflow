from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime , timedelta
import logging , requests , pendulum , json
KST = pendulum.timezone("Asia/Seoul")

#dag option init
dag = DAG(
        dag_id='upbit_bitcoin', #id option
        schedule_interval='*/60 * * * *', #(매 10분마다 실행) / schedule_interval='@daily' (time 주기)
        start_date = datetime(2022,7,8,12,1,0,tzinfo=KST), #time start / 금일부터 실행하고 싶다면 금일 전날짜로 set
        #email = ['kimuksung2@daum.net'],
        tags=['upbit_bitcoin'],
        concurrency = 3,
        max_active_runs = 2
        )

#Python
def time_setting(ts):
    #logging.info(ts)
    #UST time to KST
    ts = datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")
    ts = ts + timedelta(hours=9)
    ts = ts.isoformat()

    logging.info(ts)
    return ts

def bitcoin_collect(ts,**context):
    #time = context['task_instance'].xcom_pull(task_ids='airflow_runtime_set')
    time = ts.split('+')[0]
    logging.info(time)
    minute = "1"
    market='KRW-BTC'
    to = time+'Z'
    logging.info(to)
    count = "1"
    url = "https://api.upbit.com/v1/candles/minutes/"+minute+"?market="+market+"&to="+to+"&count="+count
    logging.info(url)
    
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    json_response = json.loads(response.text)
    
    return json_response

#DAG Task
time_set = PythonOperator(
    #task id setting
	task_id = 'airflow_runtime_set',
	#python_callable param points to the function you want to run 
	python_callable = time_setting,
	#dag param points to the DAG that this task is a part of
	dag = dag
    )

test_job = PythonOperator(
    #task id setting
	task_id = 'upbit_bitcoin_extract',
	#python_callable param points to the function you want to run 
	python_callable = bitcoin_collect,
	#dag param points to the DAG that this task is a part of
	dag = dag,
    provide_context=True
    )

#time_set >> 
test_job