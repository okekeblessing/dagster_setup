from dagster import op, job, Config
from typing import Dict, Optional
import requests
import subprocess
import os
import time


# ==============================
# Airbyte Configuration
# ==============================

AIRBYTE_BASE_URL = os.getenv(
    "AIRBYTE_BASE_URL",
    "https://unappendaged-unseized-mable.ngrok-free.dev/api/v1"
)

AIRBYTE_CONNECTION_ID = os.getenv("AIRBYTE_CONNECTION_ID", "2c403088-b6e5-4a25-8700-08491ea106df")
AIRBYTE_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAiLCJhdWQiOiJhaXJieXRlLXNlcnZlciIsInN1YiI6IjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCIsImV4cCI6MTc2Nzg2MDk0MSwicm9sZXMiOlsiQVVUSEVOVElDQVRFRF9VU0VSIiwiUkVBREVSIiwiRURJVE9SIiwiQURNSU4iLCJPUkdBTklaQVRJT05fTUVNQkVSIiwiT1JHQU5JWkFUSU9OX1JFQURFUiIsIk9SR0FOSVpBVElPTl9SVU5ORVIiLCJPUkdBTklaQVRJT05fRURJVE9SIiwiT1JHQU5JWkFUSU9OX0FETUlOIiwiV09SS1NQQUNFX1JFQURFUiIsIldPUktTUEFDRV9SVU5ORVIiLCJXT1JLU1BBQ0VfRURJVE9SIiwiV09SS1NQQUNFX0FETUlOIiwiREFUQVBMQU5FIl19.KCHYLzXwYZ-gIWb1rUfDcZwgLhkix4d3K05jchIPzos"


# ==============================
# DBT Configuration
# ==============================

class DbtConfig(Config):
    project_dir: str = "/app/dbt"
    profiles_dir: str = "/app/dbt/profiles"
    target: str = "dev"
    select: Optional[str] = None
    full_refresh: bool = False


# ==============================
# Airbyte Helpers
# ==============================

def _airbyte_headers() -> Dict:
    if not AIRBYTE_ACCESS_TOKEN:
        raise Exception("AIRBYTE_ACCESS_TOKEN is not set")

    return {
        "Authorization": f"Bearer {AIRBYTE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _get_airbyte_job(job_id: int) -> Dict:
    response = requests.post(
        f"{AIRBYTE_BASE_URL}/jobs/get",
        json={"id": job_id},
        headers=_airbyte_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["job"]


# ==============================
# Airbyte Ops
# ==============================

@op
def trigger_airbyte_sync(context) -> Dict:
    if not AIRBYTE_CONNECTION_ID:
        raise Exception("AIRBYTE_CONNECTION_ID is not set")

    response = requests.post(
        f"{AIRBYTE_BASE_URL}/connections/sync",
        json={"connectionId": AIRBYTE_CONNECTION_ID},
        headers=_airbyte_headers(),
        timeout=30,
    )
    response.raise_for_status()

    job = response.json()["job"]
    context.log.info(f"Airbyte sync triggered. Job ID: {job['id']}")

    return job


@op
def wait_for_airbyte_sync(context, job: Dict) -> Dict:
    job_id = job["id"]

    poll_interval = 30
    timeout_seconds = 3600
    elapsed = 0

    context.log.info(f"Waiting for Airbyte job {job_id} to complete")

    while elapsed < timeout_seconds:
        time.sleep(poll_interval)
        elapsed += poll_interval

        job_status = _get_airbyte_job(job_id)
        status = job_status["status"]

        context.log.info(
            f"Airbyte job {job_id} status: {status} (elapsed {elapsed}s)"
        )

        if status == "succeeded":
            return job_status

        if status in {"failed", "cancelled"}:
            raise Exception(f"Airbyte job {job_id} failed with status: {status}")

    raise TimeoutError(f"Airbyte job {job_id} timed out")


# ==============================
# DBT Ops
# ==============================

@op
def run_dbt_models(context, config: DbtConfig, airbyte_result: Dict) -> Dict:
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = config.profiles_dir

    cmd = [
        "dbt",
        "run",
        "--project-dir",
        config.project_dir,
        "--profiles-dir",
        config.profiles_dir,
        "--target",
        config.target,
    ]

    if config.select:
        cmd.extend(["--select", config.select])
    else:
        cmd.extend([
            "--select",
            "path:models/transformations/staging",
            "path:models/transformations/build",
        ])

    if config.full_refresh:
        cmd.append("--full-refresh")

    context.log.info(f"Running dbt command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=config.project_dir,
        env=env,
    )

    if result.returncode != 0:
        context.log.error(result.stdout)
        context.log.error(result.stderr)
        raise Exception("dbt run failed")

    context.log.info("dbt run completed successfully")

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


# ==============================
# Dagster Job
# ==============================

@job
def run_airbyte_sync():
    """
    Airbyte ingestion only.
    Useful for manual backfills or re-syncs.
    """
    job = trigger_airbyte_sync()
    wait_for_airbyte_sync(job)


@job
def run_dbt_transformations():
    """
    dbt transformations only.
    Assumes data already exists in the warehouse.
    """
    run_dbt_models()


@job
def execute_data_pipeline():
    """
    Full pipeline:
    1. Run Airbyte and wait
    2. Run dbt transformations
    """
    airbyte_job = trigger_airbyte_sync()
    completed_job = wait_for_airbyte_sync(airbyte_job)
    run_dbt_models(completed_job)