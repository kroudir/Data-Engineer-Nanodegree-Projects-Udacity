from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.s3_to_redshift_operator import S3ToRedshiftTransfer
from airflow.operators.check_operator import CheckOperator, ValueCheckOperator


# specify DAG default arguments
default_args = {
    'owner': 'Amir KROUDIR',
    'start_date': datetime(2019, 8, 1),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False,
    'aws_conn_id': 'aws_default',
    'postgres_conn_id': 'redshift_default',
    'redshift_conn_id': 'redshift_default',
    'params': {
        's3_bucket': 'fff-streams',
        's3_region': 'us-west-2',
        's3_json_path': None,
        'redshift_schema': 'public',
        'aws_iam_role': Variable.get("aws_iam_role")
    }
}

# define DAG
with DAG(dag_id='capstone_dag',
         description='Load and transform data data from S3 into Redshift',
         default_args=default_args,
         schedule_interval='@daily',
         template_searchpath=str(Path(__file__).parent.parent.joinpath('sql'))) as dag:

    # define tasks
    start = DummyOperator(task_id='start_execution')

    upload_raw_data = BashOperator(
        task_id='upload_raw_data_to_s3',
        bash_command='python ../upload_to_s3.py'
    )

    create_tables = PostgresOperator(
        task_id='create_tables',
        sql='create_tables.sql'
    )

    stage_tweets = S3ToRedshiftTransfer(
        task_id='stage_tweets_to_redshift',
        schema='{{ params.redshift_schema }}',
        table='staging_tweets',
        s3_bucket='{{ params.s3_bucket }}',
        s3_key='twitter_feed',
        copy_options=['COMPUPDATE OFF', 'STATUPDATE OFF', 'TRUNCATECOLUMNS']
    )

    stage_happiness = S3ToRedshiftTransfer(
        task_id='stage_happiness_to_redshift',
        schema='{{ params.redshift_schema }}',
        table='staging_happiness',
        s3_bucket='{{ params.s3_bucket }}',
        s3_key='happiness'
    )

    stage_temperature = S3ToRedshiftTransfer(
        task_id='stage_temperature_to_redshift',
        schema='{{ params.redshift_schema }}',
        table='staging_temperature',
        s3_bucket='{{ params.s3_bucket }}',
        s3_key='temperature'
    )

    check_tweets = CheckOperator(
        task_id='check_staging_tweets_table',
        sql='SELECT count(*) FROM public.staging_tweets',
        conn_id='{{ redshift_conn_id }}'
    )

    check_happiness = ValueCheckOperator(
        task_id='check_staging_happiness_table',
        sql='SELECT count(*) FROM public.staging_happiness',
        pass_value=155,
        conn_id='{{ redshift_conn_id }}'
    )

    check_temperature = ValueCheckOperator(
        task_id='check_staging_temperature_table',
        sql='SELECT count(*) FROM public.staging_temperature',
        pass_value=8235082,
        conn_id='{{ redshift_conn_id }}'
    )

    load_users_table = PostgresOperator(
        task_id='load_users_table',
        sql='users_insert.sql'
    )

    load_sources_table = PostgresOperator(
        task_id='load_sources_table',
        sql='sources_insert.sql'
    )

    load_happiness_table = PostgresOperator(
        task_id='load_happiness_table',
        sql='happiness_insert.sql'
    )

    load_temperature_table = PostgresOperator(
        task_id='load_temperature_table',
        sql='temperature_insert.sql'
    )

    load_time_table = PostgresOperator(
        task_id='load_time_table',
        sql='time_insert.sql'
    )

    load_tweets_table = PostgresOperator(
        task_id='load_tweets_fact_table',
        sql='tweets_insert.sql'
    )

    check_users = CheckOperator(
        task_id='check_users_table',
        sql='SELECT count(*) FROM public.users',
        conn_id='{{ redshift_conn_id }}'
    )

    check_sources = CheckOperator(
        task_id='check_sources_table',
        sql='SELECT count(*) FROM public.sources',
        conn_id='{{ redshift_conn_id }}'
    )

    check_happiness_dim = CheckOperator(
        task_id='check_dim_happiness_table',
        sql='SELECT count(*) FROM public.happiness',
        conn_id='{{ redshift_conn_id }}'
    )

    check_temperature_dim = CheckOperator(
        task_id='check_dim_temperature_table',
        sql='SELECT count(*) FROM public.temperature',
        conn_id='{{ redshift_conn_id }}'
    )

    check_time = CheckOperator(
        task_id='check_time_table',
        sql='SELECT count(*) FROM public.time',
        conn_id='{{ redshift_conn_id }}'
    )

    check_tweets_dim = CheckOperator(
        task_id='check_fact_tweets_table',
        sql='SELECT count(*) FROM public.tweets',
        conn_id='{{ redshift_conn_id }}'
    )

    end = DummyOperator(task_id='stop_execution')

    # define task dependencies
    staging_tasks = [stage_tweets, stage_happiness, stage_temperature]
    staging_checks = [check_tweets, check_happiness, check_temperature]
    dim_tasks = [load_users_table, load_sources_table, load_happiness_table, load_temperature_table, load_time_table]
    star_checks = [check_users, check_sources, check_happiness_dim, check_temperature_dim, check_time, check_tweets_dim]

    start >> upload_raw_data >> create_tables >> staging_tasks >> staging_checks >> dim_tasks >> load_tweets_table >> star_checks >> end
