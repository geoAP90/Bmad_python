#!/bin/bash

# Article Analyzer - Deployment Script
# This script pulls the latest code, authenticates with Docker Hub,
# and deploys the production stack.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Article Analyzer Deployment Script ===${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed. Please install it and try again.${NC}"
    exit 1
fi

# Step 1: Pull the latest code from Git
echo -e "${YELLOW}Step 1: Pulling latest code from Git...${NC}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git pull origin main
    echo -e "${GREEN}Code updated successfully!${NC}"
else
    echo -e "${YELLOW}Warning: Not a git repository. Skipping git pull.${NC}"
fi

# Step 2: Authenticate with Docker Hub
echo -e "${YELLOW}Step 2: Authenticating with Docker Hub...${NC}"
if [ -z "$DOCKERHUB_USERNAME" ] || [ -z "$DOCKERHUB_TOKEN" ]; then
    echo -e "${YELLOW}Warning: DOCKERHUB_USERNAME or DOCKERHUB_TOKEN not set in environment.${NC}"
    echo -e "${YELLOW}Attempting to login using docker login...${NC}"
    if [ -n "$DOCKERHUB_USERNAME" ]; then
        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
    else
        echo -e "${YELLOW}Please enter your Docker Hub credentials when prompted.${NC}"
        docker login
    fi
else
    echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
fi
echo -e "${GREEN}Docker Hub authentication successful!${NC}"

# Step 3: Pull the latest images from Docker Hub
echo -e "${YELLOW}Step 3: Pulling latest images from Docker Hub...${NC}"
# Force the script to use your Docker Hub identity
export DOCKERHUB_USERNAME="arpitageo06"
# Run the pull command
docker-compose -f docker-compose.prod.yml pull
echo -e "${GREEN}Images pulled successfully!${NC}"

# Step 4: Stop and remove existing containers
echo -e "${YELLOW}Step 4: Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down
echo -e "${GREEN}Containers stopped.${NC}"

# Step 5: Start the production stack
echo -e "${YELLOW}Step 5: Starting production stack...${NC}"
docker-compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}Production stack started!${NC}"

# Step 6: Prune old, dangling images to save space
echo -e "${YELLOW}Step 6: Pruning old, dangling images...${NC}"
docker image prune -f
echo -e "${GREEN}Image pruning complete!${NC}"

# Display running containers
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo -e "${GREEN}Running containers:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo -e "\n${GREEN}Article Analyzer is now deployed!${NC}"
echo -e "Backend API: http://localhost:8000"
echo -e "Frontend:   http://localhost:8501"
