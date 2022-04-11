from airflow import DAG

from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.models import Variable

import finnhub

def get_stock_price_from_finnhub(**kwargs):
    api_key = Variable.get("finnhub-api-key")
    print("api_key = ",api_key)
    finnhub_client = finnhub.Client(api_key=api_key)
    current_stock_price = finnhub_client.quote('DIS')['c']
    kwargs['task_instance'].xcom_push(key='disney_stock_price', value=str(current_stock_price))
    return str(current_stock_price)

def decide_action_from_stock_price(**kwargs):
    current_stock_price = float(kwargs["task_instance"].xcom_pull(task_ids='get_stock_price', key='disney_stock_price'))
    threshold_price = int(Variable.get("threshhold-price"))
    if current_stock_price >= threshold_price:
        return 'send_slack_notification'
    else:
        return 'no_op'


with DAG(
    'check_stock_price_dag',
    default_args={
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    max_active_runs=1,
    schedule_interval=timedelta(minutes=1),
    start_date=days_ago(1),
) as dag:

    start_node = DummyOperator(
        task_id='start_node',
        dag=dag
    )

    get_stock_price = PythonOperator(
        task_id='get_stock_price',
        python_callable=get_stock_price_from_finnhub,
        dag=dag,
    )

    check_stock_price = BranchPythonOperator(
        task_id='check_stock_price',
        python_callable=decide_action_from_stock_price,
    )

    send_slack_notification = SimpleHttpOperator(
        task_id='send_slack_notification',
        http_conn_id='http_default',
        endpoint='/services/T06GG7QA3/B03B3PJ2LRX/og1b671vsgFZhmIIK5Lohts4',
        data='{"text":"Sell stock!"}',
        headers={"Content-Type": "application/json"},
        dag=dag,
    )

    no_op = DummyOperator(
        task_id='no_op',
        dag=dag
    )

    end_node = DummyOperator(
        task_id='end_node',
        dag=dag
    )

    start_node >> get_stock_price >> check_stock_price >> [send_slack_notification,no_op] >> end_node