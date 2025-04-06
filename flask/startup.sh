#!/bin/bash
# filepath: /home/ubuntu/StockMarketDatawarehouse/flask/startup.sh

set -e

# Bring down any running containers and remove volumes
dockercompose down -v

# Build and start the containers in detached mode
dockercompose build
dockercompose up -d

# Wait for the database container to be ready
echo "Waiting for the database container to be ready..."
sleep 10

# Copy the init.sql file into the database container
docker cp init.sql flask-db-1:/tmp/

# Restore the PostgreSQL dump file to the database
docker exec -it flask-db-1 pg_restore -U postgres -d flaskdb /tmp/init.sql

echo "Database restoration completed."