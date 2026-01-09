from dagster import job
import logging
from .ops import trigger_airbyte_sync, wait_for_airbyte_sync

logger = logging.getLogger(__name__)


@job
def run_airbyte_sync():
    """
    Airbyte ingestion only.
    Useful for manual backfills or re-syncs.
    """
    logger.info("=" * 80)
    logger.info("Starting run_airbyte_sync job")
    logger.info("=" * 80)
    
    job = trigger_airbyte_sync()
    wait_for_airbyte_sync(job)
    
    logger.info("=" * 80)
    logger.info("run_airbyte_sync job completed successfully")
    logger.info("=" * 80)

