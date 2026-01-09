from dagster import job
import logging
from .ops import run_dbt_models

logger = logging.getLogger(__name__)


@job
def run_dbt_transformations():
    """
    dbt transformations only.
    Assumes data already exists in the warehouse.
    """
    logger.info("=" * 80)
    logger.info("Starting run_dbt_transformations job")
    logger.info("=" * 80)
    
    run_dbt_models()
    
    logger.info("=" * 80)
    logger.info("run_dbt_transformations job completed successfully")
    logger.info("=" * 80)

