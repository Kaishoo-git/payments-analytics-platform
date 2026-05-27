from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="Postgres to Snowflake ETL + dbt",
    start_date=datetime(2025, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["etl", "dbt", "snowflake"],
) as dag:
    
    etl_task = BashOperator(
        task_id="postgres_to_snowflake",
        bash_command=(
            "cd /opt/airflow && "
            "python scripts/postgres_to_snowflake.py "
            "--mode incremental"
        ),
    )
    
    dbt_run_task = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt run --profiles-dir /opt/airflow/dbt/.dbt"
        ),
    )
    
    etl_task >> dbt_run_task