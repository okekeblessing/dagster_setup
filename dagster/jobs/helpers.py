from typing import Dict, Optional, Any
import requests
import logging
from .constants import DEFAULT_API_TIMEOUT
from .config import AIRBYTE_BASE_URL, AIRBYTE_CLIENT_ID, AIRBYTE_CLIENT_SECRET

logger = logging.getLogger(__name__)


def _get_loggers(log_func: Optional[Any] = None):
    """
    Extracts info and error loggers from log_func or returns default loggers.
    
    Args:
        log_func: Optional logger object (e.g., context.log) with info/error methods
        
    Returns:
        Tuple of (log_info, log_error) functions
    """
    if log_func:
        log_info = log_func.info if hasattr(log_func, 'info') else log_func
        log_error = log_func.error if hasattr(log_func, 'error') else log_func
    else:
        log_info = logger.info
        log_error = logger.error
    
    return log_info, log_error


def _make_api_request(
    method: str,
    url: str,
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: int = DEFAULT_API_TIMEOUT,
    log_func: Optional[Any] = None,
) -> requests.Response:
    """
    Centralized API request handler with logging and error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full URL for the API request
        headers: Optional request headers
        json_data: Optional JSON payload
        timeout: Request timeout in seconds
        log_func: Optional logger object for Dagster context logging
        
    Returns:
        requests.Response object
        
    Raises:
        requests.exceptions.RequestException: If request fails
    """
    log_info, log_error = _get_loggers(log_func)
    
    log_info(f"Making {method.upper()} request to {url}")
    if json_data:
        log_info(f"Request payload: {json_data}")

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            timeout=timeout,
        )

        log_info(f"Response status: {response.status_code}")
        
        try:
            response_data = response.json()
            log_info(f"Response data: {response_data}")
        except ValueError:
            log_info(f"Response text: {response.text}")
        
        if response.status_code >= 400:
            log_error(f"Request failed with status {response.status_code}: {response.text}")
        else:
            log_info(f"Request successful")

        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e:
        log_error(f"API request failed: {str(e)}")
        raise


def _generate_airbyte_access_token(
    client_id: str,
    client_secret: str,
    log_func: Optional[Any] = None,
) -> str:
    """
    Generates an Airbyte access token using client credentials.
    
    Args:
        client_id: Airbyte client ID
        client_secret: Airbyte client secret
        log_func: Optional logger object for Dagster context logging
        
    Returns:
        Access token string
        
    Raises:
        Exception: If access_token not found in response
    """
    log_info, log_error = _get_loggers(log_func)
    log_info("Generating Airbyte access token")
    
    response = _make_api_request(
        method="POST",
        url=f"{AIRBYTE_BASE_URL}/applications/token",
        json_data={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={
            "accept": "application/json",
            "content-type": "application/json",
        },
        timeout=DEFAULT_API_TIMEOUT,
        log_func=log_func,
    )

    data = response.json()

    if "access_token" not in data:
        log_error("access_token not found in Airbyte response")
        log_error(f"Response data: {data}")
        raise Exception("access_token not found in Airbyte response")

    log_info("Airbyte access token generated successfully")
    return data["access_token"]


def _airbyte_headers(log_func: Optional[Any] = None) -> Dict:
    """
    Generates Airbyte API request headers with authentication.
    
    Args:
        log_func: Optional logger object for Dagster context logging
        
    Returns:
        Dictionary with Authorization and Content-Type headers
        
    Raises:
        Exception: If client credentials are not set
    """
    log_info, log_error = _get_loggers(log_func)
    
    if not AIRBYTE_CLIENT_ID or not AIRBYTE_CLIENT_SECRET:
        log_error("AIRBYTE_CLIENT_ID and AIRBYTE_CLIENT_SECRET must be set")
        raise Exception("AIRBYTE_CLIENT_ID and AIRBYTE_CLIENT_SECRET must be set")

    log_info("Generating Airbyte authentication headers")
    access_token = _generate_airbyte_access_token(
        AIRBYTE_CLIENT_ID, 
        AIRBYTE_CLIENT_SECRET, 
        log_func=log_func
    )
    
    log_info("Airbyte authentication headers generated successfully")
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def _get_airbyte_job(job_id: int, log_func: Optional[Any] = None) -> Dict:
    """
    Retrieves Airbyte job status by job ID.
    
    Args:
        job_id: Airbyte job ID
        log_func: Optional logger object for Dagster context logging
        
    Returns:
        Job dictionary with status and details
    """
    log_info, _ = _get_loggers(log_func)
    log_info(f"Fetching Airbyte job status for job ID: {job_id}")
    
    response = _make_api_request(
        method="POST",
        url=f"{AIRBYTE_BASE_URL}/jobs/get",
        json_data={"id": job_id},
        headers=_airbyte_headers(log_func=log_func),
        timeout=DEFAULT_API_TIMEOUT,
        log_func=log_func,
    )
    
    job_data = response.json()["job"]
    log_info(f"Job {job_id} retrieved successfully. Status: {job_data.get('status', 'unknown')}")
    
    return job_data

