# init docker setup
## check at least 6GB memory allocated to docker 
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.2.5/docker-compose.yaml'
docker-compose up airflow-init
docker-compose up

# Import finhub python dependency in scheduler, worker, triggerer

docker exec -it airflow_airflow-worker_1 pip install finnhub-python
docker exec -it airflow_airflow-triggerer_1 pip install finnhub-python
docker exec -it airflow_airflow-scheduler_1 pip install finnhub-python

# Move to http://localhost:8080 and login using username password as airflow.

# Set finnhub-api-key as variables in webserver with value - c982tdiad3ibrc51tnug
# Set threshhold-price as variables in webserver with value - 120

# Set 'http_default' as conn_id under new connections 
## host = https://hooks.slack.com
## connection type = HTTP
## schema = /services/T06GG7QA3/B03B3PJ2LRX/og1b671vsgFZhmIIK5Lohts4

# clear docker setup
docker-compose down --volumes --rmi all