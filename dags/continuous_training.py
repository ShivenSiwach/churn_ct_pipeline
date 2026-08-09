from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import json
import os

default_args = {
    'owner': 'ml_engineer',
    'depends_on_past': False, 
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def decide_retraining():
    report_path = "/opt/airflow/data/drift_report.json"

    if not os.path.exists(report_path):
        return "skip_retraining"

    with open(report_path, "r") as f:
        report = json.load(f)

    if report.get("drift_detection", False):
        return "retrain_model"
    else:
        return "skip_retraining"

with DAG(
    'continuous_training_pipeline',
    default_args=default_args,
    description='Automated CT Pipeline with Drift Detection',
    schedule_interval='@daily',
    catchup=False
) as dag:

    run_drift_monitor = BashOperator(
        task_id='run_drift_monitor',
        bash_command='cd /opt/airflow && python src/drift_monitor.py' 
    )

    branch_task = BranchPythonOperator(
        task_id='check_drift_status',
        python_callable=decide_retraining
    )

    retrain_model = BashOperator(
        task_id='retrain_model', 
        bash_command='cd /opt/airflow && python src/train_model.py'
    )

    skip_retraining = EmptyOperator(
        task_id='skip_retraining'
    )

    run_drift_monitor >> branch_task
    branch_task >> retrain_model
    branch_task >> skip_retraining