from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import logging

#dag option init
dag = DAG(
        dag_id='uk_dag_test_1', #id option
        schedule_interval='*/60 * * * *', #(매 10분마다 실행) / schedule_interval='@daily' (time 주기)
        start_date = datetime(2022,7,8), #time start / 금일부터 실행하고 싶다면 금일 전날짜로 set
        tags=['uksung_test']
        )

#Python
def test(**context):
    print('test function start')
    parameter=context["params"]["parameter1"]
    logging.info(parameter)
    return parameter

def test_parameter_trnasform(**context):
    transform_data = context['task_instance'].xcom_pull(task_ids='kimuksung_test')
    logging.info(transform_data)
    return True

#DAG Task
test_job = PythonOperator(
    #task id setting
	task_id = 'kimuksung_test',
	#python_callable param points to the function you want to run 
	python_callable = test,
	#dag param points to the DAG that this task is a part of
	dag = dag,  
    #parameter setting
    params = {'parameter1':'pubg'},
    #parameter on/off
    provide_context=True
    )

test_transform = PythonOperator(
    #task id setting
	task_id = 'kimuksung_transform',
	#python_callable param points to the function you want to run 
	python_callable = test_parameter_trnasform,
	#dag param points to the DAG that this task is a part of
	dag = dag,
    #parameter on/off
    provide_context=True
    )

test_job >> test_transform