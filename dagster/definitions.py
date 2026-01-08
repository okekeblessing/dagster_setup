from dagster import Definitions
from job import  run_dbt_transformations, execute_data_pipeline, run_airbyte_sync
from schedule import execute_data_pipeline_schedule

defs = Definitions(
    jobs=[run_airbyte_sync, run_dbt_transformations, execute_data_pipeline],
    schedules=[execute_data_pipeline_schedule]
)
