#!/bin/bash

# Exit if any command fails
set -e

echo "🔧 Checking for Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "🛠️ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
else
    echo "✅ Docker is already installed."
fi

echo "🔧 Checking for Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "🛠️ Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose is already installed."
fi

echo "🚀 Starting Docker containers with docker-compose..."
docker-compose up -d

# Wait for the DB container to be fully ready
echo "⏳ Waiting for the database container to be ready..."
sleep 10  # Adjust based on DB startup time

# Copy the SQL file into the container
echo "📄 Copying init.sql into flask_db container..."
docker cp flask/init.sql flask_db:/tmp/

# Run the SQL file
echo "⚙️ Executing init.sql inside the database..."
docker exec -it flask_db psql -U postgres -d flaskdb -f /tmp/flask/init.sql

# Optional: If using a dump file instead
# docker exec -it flask_db pg_restore -U postgres -d flaskdb /tmp/init.sql

echo "✅ Startup complete."