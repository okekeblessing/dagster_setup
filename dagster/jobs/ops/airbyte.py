from dagster import op
from typing import Dict
import time
import logging
from ..helpers import _make_api_request, _airbyte_headers, _get_airbyte_job
from ..config import AIRBYTE_BASE_URL, AIRBYTE_CONNECTION_ID
from ..constants import DEFAULT_API_TIMEOUT, AIRBYTE_POLL_INTERVAL, AIRBYTE_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


@op
def trigger_airbyte_sync(context) -> Dict:
    """
    Triggers an Airbyte connection sync job.
    
    Returns:
        Job dictionary with job ID and initial status
    """
    context.log.info("=" * 80)
    context.log.info("Starting Airbyte sync trigger")
    context.log.info("=" * 80)
    context.log.info(f"Connection ID: {AIRBYTE_CONNECTION_ID}")
    context.log.info(f"Base URL: {AIRBYTE_BASE_URL}")
    
    if not AIRBYTE_CONNECTION_ID:
        context.log.error("AIRBYTE_CONNECTION_ID is not set")
        raise Exception("AIRBYTE_CONNECTION_ID is not set")

    response = _make_api_request(
        method="POST",
        url=f"{AIRBYTE_BASE_URL}/connections/sync",
        json_data={"connectionId": AIRBYTE_CONNECTION_ID},
        headers=_airbyte_headers(log_func=context.log),
        timeout=DEFAULT_API_TIMEOUT,
        log_func=context.log,
    )

    job = response.json()["job"]
    job_id = job["id"]
    job_status = job.get("status", "unknown")
    
    context.log.info("=" * 80)
    context.log.info(f"Airbyte sync triggered successfully")
    context.log.info(f"Job ID: {job_id}")
    context.log.info(f"Initial Status: {job_status}")
    context.log.info(f"Job Details: {job}")
    context.log.info("=" * 80)

    return job


@op
def wait_for_airbyte_sync(context, job: Dict) -> Dict:
    """
    Polls Airbyte job status until completion or timeout.
    
    Args:
        job: Job dictionary from trigger_airbyte_sync
        
    Returns:
        Completed job dictionary with final status
        
    Raises:
        Exception: If job fails or is cancelled
        TimeoutError: If job exceeds timeout
    """
    job_id = job["id"]
    elapsed = 0

    context.log.info("=" * 80)
    context.log.info(f"Starting to wait for Airbyte job {job_id}")
    context.log.info(f"Poll interval: {AIRBYTE_POLL_INTERVAL}s")
    context.log.info(f"Timeout: {AIRBYTE_TIMEOUT_SECONDS}s")
    context.log.info("=" * 80)

    while elapsed < AIRBYTE_TIMEOUT_SECONDS:
        time.sleep(AIRBYTE_POLL_INTERVAL)
        elapsed += AIRBYTE_POLL_INTERVAL

        job_status = _get_airbyte_job(job_id, log_func=context.log)
        status = job_status["status"]

        context.log.info(
            f"Poll #{elapsed // AIRBYTE_POLL_INTERVAL} - Job {job_id} status: {status} (elapsed {elapsed}s)"
        )

        if status == "succeeded":
            context.log.info("=" * 80)
            context.log.info(f"Airbyte job {job_id} completed successfully")
            context.log.info(f"Total time: {elapsed}s")
            context.log.info(f"Final job details: {job_status}")
            context.log.info("=" * 80)
            return job_status

        if status in {"failed", "cancelled"}:
            context.log.error("=" * 80)
            context.log.error(f"Airbyte job {job_id} failed with status: {status}")
            context.log.error(f"Job details: {job_status}")
            context.log.error("=" * 80)
            raise Exception(f"Airbyte job {job_id} failed with status: {status}")

    context.log.error("=" * 80)
    context.log.error(f"Airbyte job {job_id} timed out after {AIRBYTE_TIMEOUT_SECONDS}s")
    context.log.error("=" * 80)
    raise TimeoutError(f"Airbyte job {job_id} timed out")

