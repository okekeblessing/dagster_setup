# dbt Project for NEDI

This dbt project transforms data in ClickHouse, creating analytical tables from the source tables.

## Structure

- `models/transformations/` - SQL models that transform ClickHouse data
- `profiles/profiles.yml` - ClickHouse connection configuration
- `dbt_project.yml` - dbt project configuration

## Models

1. **student_performance_summary** - Aggregates student examination performance with student and school details
2. **school_performance_metrics** - School-level performance analytics
3. **exam_analysis_by_type** - Analysis of examinations by type, year, and subject

## Running dbt

### Via Docker (dbt service)
```bash
docker-compose exec dbt dbt run --project-dir /app --profiles-dir /app/profiles
```

### Via Dagster
The `run_dbt_transformations` job in Dagster orchestrates dbt runs. It:
1. Runs all dbt models (`dbt run`)
2. Tests the models (`dbt test`)

## Configuration

Connection details are in `profiles/profiles.yml`. The host `clickhouse` refers to the ClickHouse service in docker-compose.
