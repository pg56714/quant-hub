#!/bin/sh
set -e  # Exit on any error

echo "Starting deployment..."
# Step 1: Build new image with a temporary tag
echo "Building new image..."
docker build --no-cache -t quant-hub:new .

# Step 2: Stop and remove old container if it exists
OLD_CONTAINER=$(docker ps -q -f name=quant-hub)
if [ ! -z "$OLD_CONTAINER" ]; then
    echo "Stopping and removing old container..."
    docker stop quant-hub || true
    docker rm quant-hub || true
fi

# Step 3: Start new container
echo "Starting new container..."
docker run -d --name quant-hub --restart unless-stopped quant-hub:new

# Step 4: Verify new container is running
if [ ! "$(docker ps -q -f name=quant-hub)" ]; then
    exit 1
fi

# Step 5: Clean up everything
echo "Deployment successful. Cleaning up..."
docker tag quant-hub:new quant-hub:latest
docker rmi quant-hub:new
docker system prune -f
