#!/bin/bash
#
# Simple Terminal-Bench Evaluation Runner
# Note: Terminal-Bench already runs each task in its own Docker container
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
AGENT="amplifier"
SPLIT="train"
CONCURRENT=15
MODEL=""
TIMEOUT=2.0

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
            echo "Terminal-Bench Evaluation Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --agent NAME        Agent (amplifier|baseline|both, default: amplifier)"
            echo "  --split TYPE        Tasks (small|train|test|both, default: train)"
            echo "  --concurrent N      Parallel tasks (default: 15)"
            echo "  --model NAME        Model version"
            echo "  --timeout N         Timeout multiplier (default: 2.0)"
            echo "  --help              Show this help"
            echo ""
            echo "Note: Terminal-Bench runs each task in its own Docker container"
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
echo -e "${BLUE}=== Terminal-Bench Evaluation ===${NC}"
echo -e "Agent:      ${GREEN}$AGENT${NC}"
echo -e "Split:      ${GREEN}$SPLIT${NC}"
echo -e "Concurrent: ${GREEN}$CONCURRENT${NC}"
echo -e "Timeout:    ${GREEN}${TIMEOUT}x${NC}"
if [ -n "$MODEL" ]; then
    echo -e "Model:      ${GREEN}$MODEL${NC}"
fi
echo ""

# Clean up Docker networks if needed
NETWORK_COUNT=$(docker network ls | wc -l)
if [ $NETWORK_COUNT -gt 25 ]; then
    echo -e "${YELLOW}Cleaning up Docker networks...${NC}"
    docker network prune -f
fi

# Create results directory
mkdir -p results

# Build command
CMD="uv run run_full_evaluation.py"
CMD="$CMD --agent $AGENT"
CMD="$CMD --split $SPLIT"
CMD="$CMD --concurrent $CONCURRENT"
CMD="$CMD --timeout-multiplier $TIMEOUT"

if [ -n "$MODEL" ]; then
    CMD="$CMD --model $MODEL"
fi

# Run evaluation
echo -e "${BLUE}Starting evaluation...${NC}"
echo -e "${YELLOW}Terminal-Bench will run each task in a Docker container${NC}"
echo "Command: $CMD"
echo ""

# Run and capture exit code
if $CMD; then
    echo ""
    echo -e "${GREEN}✅ Evaluation completed!${NC}"

    # Flatten the nested folder structure
    echo ""
    echo -e "${BLUE}Flattening results structure...${NC}"
    uv run utils/flatten_results.py || true

    # Run analysis
    echo ""
    echo -e "${BLUE}=== Analyzing Results ===${NC}"
    uv run analyze_terminal_bench_results.py --format text
else
    echo ""
    echo -e "${RED}❌ Evaluation failed${NC}"

    # Try to analyze anyway
    echo ""
    echo -e "${YELLOW}Attempting to analyze partial results...${NC}"
    uv run analyze_terminal_bench_results.py --format text 2>/dev/null || true
fi

# Show next steps
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. View detailed results:  ls -la results/"
echo "2. Generate report:        uv run generate_benchmark_report.py"
echo "3. AI-ready JSON:          uv run analyze_terminal_bench_results.py --format json"