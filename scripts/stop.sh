#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

NETWORK_NAME="nedi_airbyte_network"

echo "Stopping Docker Compose services and removing volumes..."
cd "$PROJECT_ROOT"
docker compose down -t 1 -v

echo "Removing Airbyte network..."
if docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  docker network rm "$NETWORK_NAME" || true
  echo "Network $NETWORK_NAME removed"
else
  echo "Network $NETWORK_NAME does not exist"
fi

echo "All services stopped and cleaned up"

