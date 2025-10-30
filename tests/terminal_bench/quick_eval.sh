#!/bin/bash
#
# Quick Terminal-Bench Evaluation Script
# Run a terminal-bench evaluation with sensible defaults
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
SPLIT="small"
CONCURRENT=3
MODEL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            SPLIT="train"
            shift
            ;;
        --test)
            SPLIT="test"
            shift
            ;;
        --baseline)
            AGENT="baseline"
            shift
            ;;
        --both)
            AGENT="both"
            shift
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --concurrent)
            CONCURRENT="$2"
            shift 2
            ;;
        --help)
            echo "Quick Terminal-Bench Evaluation"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --full       Run full training set (default: small subset)"
            echo "  --test       Run test set"
            echo "  --baseline   Use baseline agent (default: amplifier)"
            echo "  --both       Run both amplifier and baseline"
            echo "  --model NAME Specify model (e.g., claude-3-5-sonnet-latest)"
            echo "  --concurrent N  Number of concurrent trials (default: 3)"
            echo "  --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Quick test with amplifier on small subset"
            echo "  $0 --full           # Full evaluation on training set"
            echo "  $0 --both --test    # Compare both agents on test set"
            exit 0
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
echo -e "${BLUE}=== Terminal-Bench Evaluation ===${NC}"
echo -e "Agent:      ${GREEN}$AGENT${NC}"
echo -e "Split:      ${GREEN}$SPLIT${NC}"
echo -e "Concurrent: ${GREEN}$CONCURRENT${NC}"
if [ -n "$MODEL" ]; then
    echo -e "Model:      ${GREEN}$MODEL${NC}"
fi
echo ""

# Build command
CMD="uv run tests/terminal_bench/run_full_evaluation.py"
CMD="$CMD --agent $AGENT"
CMD="$CMD --split $SPLIT"
CMD="$CMD --concurrent $CONCURRENT"

if [ -n "$MODEL" ]; then
    CMD="$CMD --model $MODEL"
fi

# Create output directory if it doesn't exist
mkdir -p ai_working/tmp

# Clean up old Docker networks if needed
NETWORK_COUNT=$(docker network ls | wc -l)
if [ $NETWORK_COUNT -gt 30 ]; then
    echo -e "${YELLOW}Cleaning up Docker networks...${NC}"
    docker network prune -f
fi

# Run evaluation
echo -e "${BLUE}Starting evaluation...${NC}"
echo "Command: $CMD"
echo ""

# Run and capture exit code
if $CMD; then
    echo ""
    echo -e "${GREEN}✅ Evaluation completed successfully!${NC}"

    # Find the latest run directory
    LATEST_RUN=$(ls -t ai_working/tmp | grep -E "^${AGENT}_${SPLIT}_" | head -1)
    if [ -n "$LATEST_RUN" ]; then
        echo ""
        echo -e "${BLUE}Results saved to: ai_working/tmp/$LATEST_RUN${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Monitor progress:  uv run tests/terminal_bench/monitor_evaluation.py"
        echo "  2. Generate report:   uv run tests/terminal_bench/generate_benchmark_report.py --run-dir ai_working/tmp/$LATEST_RUN"
        echo "  3. View dashboard:    uv run tests/terminal_bench/generate_eval_dashboard.py"
    fi
else
    echo ""
    echo -e "${RED}❌ Evaluation failed${NC}"
    exit 1
fi