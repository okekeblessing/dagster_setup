import pandas as pd
from sqlalchemy import create_engine
from decouple import config
import os

# PostgreSQL connection
from sqlalchemy.ext.asyncio import create_async_engine

# Load PostgreSQL configuration from environment
POSTGRES_USER = config("POSTGRES_USER", default="myuser")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", default="mypassword")
POSTGRES_HOST = config("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = config("POSTGRES_PORT", default="5432", cast=int)
POSTGRES_DB = config("POSTGRES_DB", default="nedi")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)

# Note: if_exists='replace' will create tables if they don't exist,
# or replace them if they do exist. This script works whether tables exist or not.

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
files_dir = os.path.join(script_dir, 'files')

# Import Schools
schools_df = pd.read_csv(os.path.join(files_dir, 'schools.csv'))
schools_df.to_sql('schools', engine, if_exists='replace', index=False)

# Import Teachers
teachers_df = pd.read_csv(os.path.join(files_dir, 'teachers.csv'))
teachers_df.to_sql('teachers', engine, if_exists='replace', index=False)

# Import Students
students_df = pd.read_csv(os.path.join(files_dir, 'students.csv'))
students_df.to_sql('students', engine, if_exists='replace', index=False)

# Import Examinations
examinations_df = pd.read_csv(os.path.join(files_dir, 'examinations.csv'))
examinations_df.to_sql('examinations', engine, if_exists='replace', index=False)

print("All CSV files imported successfully into PostgreSQL!")
