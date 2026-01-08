FROM python:3.12-slim

WORKDIR /app

# Install dbt and ClickHouse adapter
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dbt project files
COPY dbt_project.yml .
COPY profiles/ ./profiles/
COPY models/ ./models/
COPY scripts/ ./scripts/

# Set dbt profile path
ENV DBT_PROFILES_DIR=/app/profiles

# Make scripts executable
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

CMD ["dbt", "--version"]


