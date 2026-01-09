from dagster import Config
from typing import Optional
from decouple import config
from .constants import DBT_DEFAULT_PROJECT_DIR, DBT_DEFAULT_PROFILES_DIR, DBT_DEFAULT_TARGET

AIRBYTE_BASE_URL = config(
    "AIRBYTE_BASE_URL",
    default="https://unappendaged-unseized-mable.ngrok-free.dev/api/v1"
)
AIRBYTE_CONNECTION_ID = config("AIRBYTE_CONNECTION_ID", default="2c403088-b6e5-4a25-8700-08491ea106df")
AIRBYTE_CLIENT_ID = config("AIRBYTE_CLIENT_ID", default="")
AIRBYTE_CLIENT_SECRET = config("AIRBYTE_CLIENT_SECRET", default="")


class DbtConfig(Config):
    project_dir: str = DBT_DEFAULT_PROJECT_DIR
    profiles_dir: str = DBT_DEFAULT_PROFILES_DIR
    target: str = DBT_DEFAULT_TARGET
    select: Optional[str] = None
    full_refresh: bool = False

