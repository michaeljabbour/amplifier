#!/bin/bash
#
# Clean up Docker resources and restart evaluation
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Docker Cleanup Script ===${NC}"
echo ""

# Stop all Terminal-Bench containers
echo -e "${YELLOW}Stopping Terminal-Bench containers...${NC}"
docker ps --format '{{.Names}}' | grep -E "amplifier_train|amplifier_test|amplifier_small" | xargs -r docker stop || true

# Remove stopped containers
echo -e "${YELLOW}Removing stopped containers...${NC}"
docker container prune -f

# Clean up networks
echo -e "${YELLOW}Cleaning up Docker networks...${NC}"
docker network prune -f

# Clean up volumes (optional - be careful)
echo -e "${YELLOW}Cleaning up unused volumes...${NC}"
docker volume prune -f

# Show current status
echo ""
echo -e "${GREEN}Current Docker status:${NC}"
echo "Containers: $(docker ps | wc -l)"
echo "Networks: $(docker network ls | wc -l)"
echo "Memory usage:"
docker system df

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo -e "${BLUE}Recommended next steps:${NC}"
echo "1. Use lower concurrency: ./run_eval.sh --split train --concurrent 8"
echo "2. Or run in smaller batches: ./run_eval.sh --split small --concurrent 5"
echo "3. Monitor resources: docker stats"