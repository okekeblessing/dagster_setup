from dagster import ScheduleDefinition, DefaultScheduleStatus
from jobs import execute_data_pipeline

execute_data_pipeline_schedule = ScheduleDefinition(
    name="execute_data_pipeline",
    job=execute_data_pipeline,
    cron_schedule="*/10 * * * *",
    default_status=DefaultScheduleStatus.RUNNING,
    description="Execute the data pipeline"
)
