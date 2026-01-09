# Data Pipeline Architecture

## Overview

This project implements a data pipeline that extracts data from PostgreSQL via FastAPI, loads it into ClickHouse using Airbyte, and transforms it with dbt. Dagster orchestrates the workflow.

## Data Flow

### FastAPI to ClickHouse via Airbyte

FastAPI exposes PostgreSQL data through REST endpoints. Airbyte connects to FastAPI as a source, extracts data from the endpoints, and loads it into ClickHouse staging tables. The data is stored in ClickHouse for further processing.

### ClickHouse to ClickHouse via dbt

dbt reads from ClickHouse staging tables, applies transformations like joins and aggregations, and writes the transformed data to ClickHouse build tables. The final analytics-ready data is available in ClickHouse build tables.

## Dagster Orchestrator

Dagster manages the entire data pipeline workflow. It coordinates when to run Airbyte syncs and when to execute dbt transformations.

Dagster has three main parts. Operations are the building blocks that perform specific tasks. Jobs combine operations into workflows. The scheduler automatically runs jobs on a schedule.

The trigger operation starts an Airbyte sync job by making an API call to Airbyte. The wait operation polls the job status every 10 seconds until it completes, with a timeout of 5 minutes. The run operation executes dbt models that transform data from staging tables to build tables.

The execute data pipeline job runs the complete workflow. It first triggers an Airbyte sync to extract data from FastAPI and load it into ClickHouse. Then it waits for the sync to complete. Finally, it runs dbt transformations to process the data into analytics-ready tables.

The scheduler automatically runs the execute data pipeline job every 10 minutes. This ensures data is regularly synced and transformed without manual intervention.

## Setup Service

The setup service initializes the databases and loads seed data when the system starts. It creates the ClickHouse analytics database and tables for examinations, teachers, students, and schools. It also loads sample data from CSV files into PostgreSQL for testing purposes. This service runs once at startup and waits for both PostgreSQL and ClickHouse to be healthy before executing.

## FastAPI

FastAPI exposes PostgreSQL data through REST API endpoints. It provides four GET endpoints that return data from the PostgreSQL database. The examinations endpoint returns all examination records. The teachers endpoint returns all teacher records. The schools endpoint returns all school records. The students endpoint returns all student records.

FastAPI uses SQLAlchemy ORM to query PostgreSQL and returns JSON responses. It connects to PostgreSQL using a connection pool and is accessible on port 8001.

## ClickHouse

ClickHouse serves as the data warehouse for analytics. The setup service creates the analytics database and staging tables for examinations, teachers, students, and schools. These staging tables receive raw data from Airbyte.

dbt creates build tables that contain transformed analytics-ready data. These include student profiles with aggregations, student exam summaries, school performance metrics, and teacher subject summaries.

ClickHouse exposes three ports. Port 8123 provides the HTTP interface. Port 9001 provides the native protocol. Port 9009 provides interserver and gRPC communication. Data is stored in persistent volumes to ensure retention across container restarts.

## dbt

dbt transforms data within ClickHouse using SQL. It has two types of models. Staging models clean and standardize raw data from the staging tables. Build models create analytics-ready tables with joins, aggregations, and calculations.

The staging models process raw data from examinations, teachers, students, and schools tables. The build models create student profiles, exam summaries, school performance metrics, and teacher performance metrics.

dbt reads from staging tables, applies SQL transformations, and writes to build tables. It uses the ClickHouse adapter to execute queries directly in ClickHouse.

## Network Architecture

The system uses two bridge networks to organize services.

The database network connects database services and applications. It includes postgres, clickhouse, fastapi, pgadmin, clickhouse UI, setup service, and dbt. This network allows these services to communicate with each other while keeping them separate from orchestration services.

The dagster network connects Dagster services for orchestration. It includes dagster PostgreSQL, dagster webserver, dagster daemon, dagster user code, and dbt. This network keeps orchestration services separate from data services.

Network isolation provides security boundaries. Services only connect to networks they need, reducing unnecessary communication paths.

## External Services

### Airbyte

Airbyte cannot run in Docker Compose due to complex dependencies. Instead, it runs using abctl, which is the Airbyte Control Plane for management. The abctl container runs separately from the Docker Compose stack.

To allow Docker services to communicate with Airbyte, ngrok is used as a reverse proxy. Ngrok creates a public URL for the Airbyte API, allowing Docker services to reach Airbyte even though it runs outside the Docker Compose network.

The Airbyte container is connected to a custom network called nedi_airbyte_network via a setup script. This enables communication between Airbyte, FastAPI, and ClickHouse.

Airbyte configuration includes the ngrok public URL as the base URL, a pre-configured connection ID, and authentication credentials including client ID and client secret.

## Quick Start

### Install Airbyte

You can install Airbyte using any method that works for your environment. This includes using abctl, Docker directly, or any other installation method. The important requirement is that Airbyte must be accessible from any network host, meaning it needs to be exposed on a public network or accessible via a public URL.

Once Airbyte is installed and running, you need to set up a reverse proxy to expose it publicly. Use ngrok or any similar reverse proxy service to create a public URL for your Airbyte instance. This public URL will be used by Docker services to communicate with Airbyte.

Configure the public URL in your `.env` file as the `AIRBYTE_BASE_URL`. Also set your `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` in the `.env` file for authentication.

### Start Docker Services

To start all services, run the start script. This builds and starts all Docker containers, waits for them to be ready, and sets up Airbyte network connections.

```bash
./scripts/start.sh
```

To stop all services, run the stop script. This stops all containers, removes volumes, and cleans up networks.

```bash
./scripts/stop.sh
```

Services are accessible at the following addresses:

- **FastAPI**: http://localhost:8001
- **Dagster UI**: http://localhost:3000
- **pgAdmin**: http://localhost:5050
- **ClickHouse UI**: http://localhost:5521

### Configure Airbyte Connection

After all services are started, you need to configure Airbyte for the first time. Open the Airbyte UI and create a new source connection. Use the Airbyte builder to create a custom source that fetches data from FastAPI endpoints. Configure the source to connect to your FastAPI instance at the appropriate endpoint URLs.

Create a destination connection in Airbyte. Set the destination type to ClickHouse and configure it with your ClickHouse connection details including host, port, database, username, and password.

Create a connection in Airbyte that links your FastAPI source to your ClickHouse destination. Configure the sync update type and any other connection settings as needed. Save the connection and note the connection ID, then update the `AIRBYTE_CONNECTION_ID` in your `.env` file.

### Execute Dagster Jobs

Once the Airbyte connection is configured and tested, you can execute Dagster jobs. Open the Dagster UI at localhost port 3000 and navigate to the Jobs section. You can manually trigger the execute data pipeline job, or wait for the scheduler to run it automatically every 10 minutes.

The job will trigger the Airbyte sync to extract data from FastAPI and load it into ClickHouse, then run dbt transformations to process the data into analytics-ready tables.

## Environment Variables

The `.env` file contains all configuration variables. Each variable includes comments indicating which services use it. This makes it easy to understand what each configuration affects.

## Architecture Summary

Data flows from FastAPI which exposes PostgreSQL data. Airbyte extracts this data and loads it into ClickHouse staging tables. dbt then transforms the data from staging tables to build tables. Dagster orchestrates the entire workflow, triggering Airbyte syncs and dbt transformations in the correct order. The scheduler ensures this happens automatically every 10 minutes.
