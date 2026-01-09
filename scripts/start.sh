#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Starting Docker Compose services..."
cd "$PROJECT_ROOT"
docker compose up --build -d

echo "Waiting for containers to be ready..."
FASTAPI_CONTAINER_NAME="fastapi_app"
CLICKHOUSE_CONTAINER_NAME="clickhouse_db"
AIRBYTE_CONTAINER_NAME="airbyte-abctl-control-plane"

MAX_WAIT=120
ELAPSED=0
INTERVAL=2

wait_for_container() {
  local container_name=$1
  while [ $ELAPSED -lt $MAX_WAIT ]; do
    if docker ps -qf "name=^${container_name}$" | grep -q .; then
      echo "$container_name is running"
      return 0
    fi
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
  done
  echo "Timeout waiting for $container_name"
  return 1
}

ELAPSED=0
wait_for_container "$FASTAPI_CONTAINER_NAME"

ELAPSED=0
wait_for_container "$CLICKHOUSE_CONTAINER_NAME"

ELAPSED=0
wait_for_container "$AIRBYTE_CONTAINER_NAME"

echo "Setting up Airbyte network..."
"$SCRIPT_DIR/setup_airbyte_network.sh"

echo "All services started successfully"

