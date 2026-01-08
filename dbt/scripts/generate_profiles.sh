#!/bin/bash
# Generate profiles.yml from environment variables

cat > /app/profiles/profiles.yml << EOF
nedi_clickhouse:
  target: dev
  outputs:
    dev:
      type: clickhouse
      schema: analytics
      host: \${CLICKHOUSE_HOST:-clickhouse}
      port: \${CLICKHOUSE_PORT:-9000}
      user: \${CLICKHOUSE_USER:-default}
      password: \${CLICKHOUSE_PASSWORD:-yourpassword}
      database: analytics
      driver: native
      secure: false
EOF

# Replace environment variables
sed -i "s|\\\${CLICKHOUSE_HOST:-clickhouse}|${CLICKHOUSE_HOST:-clickhouse}|g" /app/profiles/profiles.yml
sed -i "s|\\\${CLICKHOUSE_PORT:-9000}|${CLICKHOUSE_PORT:-9000}|g" /app/profiles/profiles.yml
sed -i "s|\\\${CLICKHOUSE_USER:-default}|${CLICKHOUSE_USER:-default}|g" /app/profiles/profiles.yml
sed -i "s|\\\${CLICKHOUSE_PASSWORD:-yourpassword}|${CLICKHOUSE_PASSWORD:-yourpassword}|g" /app/profiles/profiles.yml


