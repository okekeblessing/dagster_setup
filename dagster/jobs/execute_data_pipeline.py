from dagster import job
import logging
from .ops import trigger_airbyte_sync, wait_for_airbyte_sync, run_dbt_models

logger = logging.getLogger(__name__)


@job
def execute_data_pipeline():
    """
    Full pipeline:
    1. Run Airbyte and wait
    2. Run dbt transformations
    """
    logger.info("=" * 80)
    logger.info("Starting execute_data_pipeline job")
    logger.info("Pipeline steps: 1. Airbyte sync, 2. dbt transformations")
    logger.info("=" * 80)
    
    logger.info("Step 1/2: Triggering Airbyte sync")
    airbyte_job = trigger_airbyte_sync()
    
    logger.info("Step 1/2: Waiting for Airbyte sync to complete")
    completed_job = wait_for_airbyte_sync(airbyte_job)
    logger.info("Step 1/2: Airbyte sync completed")
    
    logger.info("Step 2/2: Starting dbt transformations")
    run_dbt_models(completed_job)
    logger.info("Step 2/2: dbt transformations completed")
    
    logger.info("=" * 80)
    logger.info("execute_data_pipeline job completed successfully")
    logger.info("=" * 80)

