from dagster import op
from typing import Dict, Optional, Any
import subprocess
import os
import logging
from ..helpers import _get_loggers
from ..config import DbtConfig

logger = logging.getLogger(__name__)


def _build_dbt_command(config: DbtConfig, log_func: Optional[Any] = None) -> list:
    """
    Builds dbt run command based on configuration.
    
    Args:
        config: DbtConfig object with dbt settings
        log_func: Optional logger object for Dagster context logging
        
    Returns:
        List of command arguments for subprocess
    """
    log_info, _ = _get_loggers(log_func)
    log_info("Building dbt command from configuration")
    
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
        log_info(f"Using custom select: {config.select}")
    else:
        cmd.extend([
            "--select",
            "path:models/transformations/staging",
            "path:models/transformations/build",
        ])
        log_info("Using default select paths: staging + build")

    if config.full_refresh:
        cmd.append("--full-refresh")
        log_info("Full refresh mode enabled")

    log_info(f"Built dbt command with {len(cmd)} arguments")
    return cmd


@op
def run_dbt_models(context, config: DbtConfig, airbyte_result: Dict) -> Dict:
    """
    Executes dbt models transformation.
    
    Args:
        config: DbtConfig object with dbt settings
        airbyte_result: Result from Airbyte sync (used for dependency tracking)
        
    Returns:
        Dictionary with stdout and stderr from dbt execution
        
    Raises:
        Exception: If dbt run fails
    """
    context.log.info("=" * 80)
    context.log.info("Starting dbt models execution")
    context.log.info("=" * 80)
    context.log.info(f"Project directory: {config.project_dir}")
    context.log.info(f"Profiles directory: {config.profiles_dir}")
    context.log.info(f"Target: {config.target}")
    context.log.info(f"Select: {config.select or 'default (staging + build)'}")
    context.log.info(f"Full refresh: {config.full_refresh}")
    
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = config.profiles_dir
    context.log.info(f"DBT_PROFILES_DIR set to: {config.profiles_dir}")

    cmd = _build_dbt_command(config, log_func=context.log)
    context.log.info(f"Executing dbt command: {' '.join(cmd)}")
    context.log.info("=" * 80)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=config.project_dir,
        env=env,
    )

    context.log.info(f"dbt process completed with return code: {result.returncode}")

    if result.returncode != 0:
        context.log.error("=" * 80)
        context.log.error("dbt run failed")
        context.log.error("=" * 80)
        context.log.error("STDOUT:")
        context.log.error(result.stdout)
        context.log.error("=" * 80)
        context.log.error("STDERR:")
        context.log.error(result.stderr)
        context.log.error("=" * 80)
        raise Exception("dbt run failed")

    context.log.info("=" * 80)
    context.log.info("dbt run completed successfully")
    context.log.info("=" * 80)
    context.log.info("STDOUT:")
    context.log.info(result.stdout)
    if result.stderr:
        context.log.info("STDERR:")
        context.log.info(result.stderr)
    context.log.info("=" * 80)

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

