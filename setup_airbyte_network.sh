#!/bin/sh
set -e

NETWORK_NAME="nedi_airbyte_network"
FASTAPI_CONTAINER_NAME="fastapi_app"
CLICKHOUSE_CONTAINER_NAME="clickhouse_db"
EXTERNAL_CONTAINER_ID="bea06cd8160c81ea266e300e48a4d6b4012d84292de827b9c750714993e264c9"

echo "Fetching container IDs..."

FASTAPI_ID=$(docker ps -qf "name=^${FASTAPI_CONTAINER_NAME}$")
CLICKHOUSE_ID=$(docker ps -qf "name=^${CLICKHOUSE_CONTAINER_NAME}$")

if [ -z "$FASTAPI_ID" ]; then
  echo "fastapi container not found"
  exit 1
fi

if [ -z "$CLICKHOUSE_ID" ]; then
  echo "clickhouse container not found"
  exit 1
fi

echo "fastapi_app container ID: $FASTAPI_ID"
echo "clickhouse_db container ID: $CLICKHOUSE_ID"

if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "Creating network: $NETWORK_NAME"
  docker network create "$NETWORK_NAME"
else
  echo "Network $NETWORK_NAME already exists"
fi

echo "Connecting containers to $NETWORK_NAME"

docker network connect "$NETWORK_NAME" "$FASTAPI_ID" 2>/dev/null || true
docker network connect "$NETWORK_NAME" "$CLICKHOUSE_ID" 2>/dev/null || true
docker network connect "$NETWORK_NAME" "$EXTERNAL_CONTAINER_ID" 2>/dev/null || true

echo "All containers are connected to $NETWORK_NAME"