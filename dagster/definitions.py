from dagster import Definitions
from jobs import run_dbt_transformations, execute_data_pipeline, run_airbyte_sync
from schedule import execute_data_pipeline_schedule

defs = Definitions(
    jobs=[execute_data_pipeline],
    schedules=[execute_data_pipeline_schedule]
)
