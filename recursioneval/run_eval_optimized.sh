#!/bin/bash
#
# Optimized Terminal-Bench Evaluation Runner
# Handles timeouts and resource management better
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values - optimized for stability
AGENT="amplifier"
SPLIT="train"
CONCURRENT=6  # Lower for stability
MODEL=""
TIMEOUT=3.0   # Higher timeout for Amplifier's recursive reasoning

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent)
            AGENT="$2"
            shift 2
            ;;
        --split)
            SPLIT="$2"
            shift 2
            ;;
        --concurrent)
            CONCURRENT="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --help)
            echo "Optimized Terminal-Bench Evaluation Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --agent NAME        Agent (amplifier|baseline|both, default: amplifier)"
            echo "  --split TYPE        Tasks (small|train|test|both, default: train)"
            echo "  --concurrent N      Parallel tasks (default: 6, recommended: 4-8)"
            echo "  --model NAME        Model version"
            echo "  --timeout N         Timeout multiplier (default: 3.0 for Amplifier)"
            echo "  --help              Show this help"
            echo ""
            echo "Optimizations:"
            echo "  - Lower concurrency (6) for stability"
            echo "  - Higher timeout (3.0x = 18 min/task) for Amplifier"
            echo "  - Auto Docker cleanup every 10 tasks"
            echo "  - Resource monitoring"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
    echo "export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

# Display configuration
echo -e "${BLUE}=== Optimized Terminal-Bench Evaluation ===${NC}"
echo -e "Agent:      ${GREEN}$AGENT${NC}"
echo -e "Split:      ${GREEN}$SPLIT${NC}"
echo -e "Concurrent: ${GREEN}$CONCURRENT${NC} (optimized for stability)"
echo -e "Timeout:    ${GREEN}${TIMEOUT}x${NC} ($(echo "$TIMEOUT * 360" | bc -l | cut -d. -f1) seconds per task)"
if [ -n "$MODEL" ]; then
    echo -e "Model:      ${GREEN}$MODEL${NC}"
fi
echo ""

# Warning about timeouts
if [ "$AGENT" = "amplifier" ]; then
    echo -e "${YELLOW}⚠️  Note: Amplifier uses recursive reasoning which takes longer${NC}"
    echo -e "${YELLOW}   Each task may take up to $(echo "$TIMEOUT * 6" | bc -l | cut -d. -f1) minutes${NC}"
    echo ""
fi

# Pre-cleanup to ensure clean state
echo -e "${YELLOW}Pre-cleaning Docker resources...${NC}"
docker network prune -f > /dev/null 2>&1
docker container prune -f > /dev/null 2>&1

# Monitor Docker resources
echo -e "${BLUE}Current Docker status:${NC}"
echo "Networks: $(docker network ls | wc -l)/30 max"
echo "Containers: $(docker ps -a | wc -l)"
echo ""

# Create results directory
mkdir -p results

# Build command with optimized parameters
CMD="uv run run_full_evaluation.py"
CMD="$CMD --agent $AGENT"
CMD="$CMD --split $SPLIT"
CMD="$CMD --concurrent $CONCURRENT"
CMD="$CMD --timeout-multiplier $TIMEOUT"

if [ -n "$MODEL" ]; then
    CMD="$CMD --model $MODEL"
fi

# Function to monitor resources
monitor_resources() {
    while true; do
        NETWORKS=$(docker network ls | wc -l)
        CONTAINERS=$(docker ps | wc -l)

        if [ $NETWORKS -gt 25 ]; then
            echo -e "\n${YELLOW}⚠️  Network limit approaching ($NETWORKS/30), cleaning...${NC}"
            docker network prune -f > /dev/null 2>&1
        fi

        if [ $CONTAINERS -gt 20 ]; then
            echo -e "\n${YELLOW}⚠️  High container count ($CONTAINERS), may need cleanup${NC}"
        fi

        sleep 30
    done
}

# Start resource monitor in background
monitor_resources &
MONITOR_PID=$!

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    kill $MONITOR_PID 2>/dev/null || true
    docker container prune -f > /dev/null 2>&1
    docker network prune -f > /dev/null 2>&1
}

# Set trap for cleanup
trap cleanup EXIT

# Run evaluation
echo -e "${BLUE}Starting optimized evaluation...${NC}"
echo -e "${YELLOW}This will take approximately $(echo "$TIMEOUT * 6 * 39 / 60" | bc -l | cut -d. -f1) hours for 39 tasks${NC}"
echo "Command: $CMD"
echo ""

# Run with timeout handling
if timeout --preserve-status $(echo "$TIMEOUT * 3600 * 2" | bc) $CMD; then
    echo ""
    echo -e "${GREEN}✅ Evaluation completed!${NC}"

    # Flatten results
    echo ""
    echo -e "${BLUE}Flattening results structure...${NC}"
    uv run utils/flatten_results.py || true

    # Run analysis
    echo ""
    echo -e "${BLUE}=== Analyzing Results ===${NC}"
    uv run analyze_terminal_bench_results.py --format text
else
    EXIT_CODE=$?
    echo ""

    if [ $EXIT_CODE -eq 124 ]; then
        echo -e "${RED}❌ Evaluation timed out after $(echo "$TIMEOUT * 2" | bc) hours${NC}"
    else
        echo -e "${RED}❌ Evaluation failed with exit code $EXIT_CODE${NC}"
    fi

    # Try to analyze partial results
    echo ""
    echo -e "${YELLOW}Attempting to analyze partial results...${NC}"
    uv run analyze_terminal_bench_results.py --format text 2>/dev/null || true
fi

# Kill monitor
kill $MONITOR_PID 2>/dev/null || true

# Final cleanup
echo ""
echo -e "${BLUE}Final Docker cleanup...${NC}"
docker container prune -f
docker network prune -f

# Show summary
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "- Results saved in: results/"
echo "- View details: uv run analyze_terminal_bench_results.py"
echo "- Generate report: uv run generate_benchmark_report.py"

# Recommendations
echo ""
echo -e "${BLUE}If timeouts persist, try:${NC}"
echo "1. Increase timeout: --timeout 4.0 (24 min/task)"
echo "2. Reduce concurrency: --concurrent 4"
echo "3. Run smaller batches: --split small"
echo "4. Use baseline agent: --agent baseline (faster)"