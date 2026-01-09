from decouple import config

# PostgreSQL Configuration
POSTGRES_USER = config("POSTGRES_USER", default="myuser")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", default="mypassword")
POSTGRES_DB = config("POSTGRES_DB", default="nedi")
POSTGRES_HOST = config("POSTGRES_HOST", default="postgres")
POSTGRES_PORT = config("POSTGRES_PORT", default="5432", cast=int)

# Database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

