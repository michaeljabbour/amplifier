#!/bin/bash
#
# Dockerized Terminal-Bench Evaluation Runner
# Provides isolated, parallel task execution with resource management
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
export AGENT="amplifier"
export SPLIT="small"
export CONCURRENT_TASKS=10
export TIMEOUT_MULTIPLIER=2.0
MONITORING=false
BUILD_FRESH=false
CLEANUP_AFTER=false

# Function to show usage
show_usage() {
    echo "Dockerized Terminal-Bench Evaluation"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --agent NAME        Agent to evaluate (amplifier|baseline|both, default: amplifier)"
    echo "  --split TYPE        Task split (small|train|test|both, default: small)"
    echo "  --concurrent N      Number of parallel tasks (default: 10)"
    echo "  --timeout N         Timeout multiplier (default: 2.0)"
    echo "  --monitor           Enable resource monitoring"
    echo "  --build             Force rebuild Docker images"
    echo "  --cleanup           Clean up Docker resources after run"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Quick test with defaults"
    echo "  $0 --split train --concurrent 15      # Full training set with 15 parallel tasks"
    echo "  $0 --agent both --monitor              # Compare agents with monitoring"
    echo "  $0 --build --cleanup                   # Fresh build and cleanup after"
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            export AGENT="$2"
            shift 2
            ;;
        --split)
            export SPLIT="$2"
            shift 2
            ;;
        --concurrent)
            export CONCURRENT_TASKS="$2"
            shift 2
            ;;
        --timeout)
            export TIMEOUT_MULTIPLIER="$2"
            shift 2
            ;;
        --monitor)
            MONITORING=true
            shift
            ;;
        --build)
            BUILD_FRESH=true
            shift
            ;;
        --cleanup)
            CLEANUP_AFTER=true
            shift
            ;;
        --help)
            show_usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY environment variable is not set${NC}"
    echo "Please set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Display configuration
echo -e "${BLUE}=== Dockerized Terminal-Bench Evaluation ===${NC}"
echo -e "Agent:          ${GREEN}$AGENT${NC}"
echo -e "Split:          ${GREEN}$SPLIT${NC}"
echo -e "Concurrent:     ${GREEN}$CONCURRENT_TASKS${NC}"
echo -e "Timeout:        ${GREEN}${TIMEOUT_MULTIPLIER}x${NC}"
echo -e "Monitoring:     ${GREEN}$MONITORING${NC}"
echo ""

# Check Docker daemon
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Determine docker-compose command (plugin vs standalone)
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose and try again"
    echo "See: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}Using: $DOCKER_COMPOSE${NC}"

# Clean up any existing containers
echo -e "${YELLOW}Cleaning up existing containers...${NC}"
$DOCKER_COMPOSE down 2>/dev/null || true

# Clean up Docker networks if needed
NETWORK_COUNT=$(docker network ls | wc -l)
if [ $NETWORK_COUNT -gt 25 ]; then
    echo -e "${YELLOW}Cleaning up Docker networks...${NC}"
    docker network prune -f
fi

# Build images if requested or if they don't exist
if [ "$BUILD_FRESH" = true ] || ! docker images | grep -q "recursioneval"; then
    echo -e "${BLUE}Building Docker images...${NC}"
    $DOCKER_COMPOSE build --no-cache
else
    echo -e "${BLUE}Using existing Docker images${NC}"
fi

# Create results directory
mkdir -p results

# Determine profile to use
COMPOSE_PROFILES=""
if [ "$MONITORING" = true ]; then
    COMPOSE_PROFILES="--profile monitoring"
fi

# Run evaluation
echo ""
echo -e "${BLUE}Starting evaluation...${NC}"
echo -e "${YELLOW}This will run in Docker containers for better isolation${NC}"
echo ""

# Start services
if [ "$MONITORING" = true ]; then
    # Start with monitoring in background
    $DOCKER_COMPOSE $COMPOSE_PROFILES up -d monitor
    echo -e "${GREEN}✓ Resource monitor started${NC}"
fi

# Run main evaluation
$DOCKER_COMPOSE $COMPOSE_PROFILES up evaluator

# Check exit code
EVAL_EXIT_CODE=$?

if [ $EVAL_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Evaluation completed successfully!${NC}"

    # Run analysis
    echo ""
    echo -e "${BLUE}=== Analyzing Results ===${NC}"
    docker run --rm -v $(pwd):/app -w /app recursioneval:latest \
        uv run analyze_terminal_bench_results.py --format text
else
    echo ""
    echo -e "${RED}❌ Evaluation failed with exit code $EVAL_EXIT_CODE${NC}"
fi

# Cleanup if requested
if [ "$CLEANUP_AFTER" = true ]; then
    echo ""
    echo -e "${YELLOW}Cleaning up Docker resources...${NC}"
    $DOCKER_COMPOSE down -v
    docker system prune -f
    echo -e "${GREEN}✓ Cleanup complete${NC}"
else
    echo ""
    echo -e "${BLUE}Docker containers are still running.${NC}"
    echo "To stop them: $DOCKER_COMPOSE down"
    echo "To view logs: $DOCKER_COMPOSE logs"
fi

# Show next steps
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. View results:     ls -la results/"
echo "2. Generate report:  uv run generate_benchmark_report.py"
echo "3. View dashboard:   uv run generate_eval_dashboard.py"

exit $EVAL_EXIT_CODE