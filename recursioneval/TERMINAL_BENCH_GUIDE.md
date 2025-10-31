# Terminal-Bench Evaluation Guide for Amplifier

## Overview

Terminal-Bench is a comprehensive benchmark suite that evaluates LLM agents on real-world terminal-based tasks. This guide explains how to run full evaluations of Amplifier using Terminal-Bench.

## Complete Evaluation Workflow

### 1. Prerequisites

Ensure all dependencies are installed:
```bash
# Install terminal-bench
uv pip install terminal-bench

# Verify Docker is running
docker --version

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### 2. Quick Test Run

Start with a small test to verify everything works:
```bash
./tests/terminal_bench/quick_eval.sh
```

This runs 5 tasks and should complete in ~10-15 minutes.

### 3. Full Evaluation

Run the complete evaluation suite:

#### Option A: Using Quick Eval Script (Recommended)
```bash
# Full training set evaluation
./tests/terminal_bench/quick_eval.sh --full

# Test set evaluation
./tests/terminal_bench/quick_eval.sh --test

# Compare amplifier vs baseline
./tests/terminal_bench/quick_eval.sh --both --full
```

#### Option B: Using Full Evaluation Script
```bash
# More control over parameters
uv run tests/terminal_bench/run_full_evaluation.py \
  --agent amplifier \
  --split train \
  --concurrent 5 \
  --attempts 1 \
  --model claude-sonnet-4-5
```

### 4. Monitor Progress

In a separate terminal, monitor the evaluation:
```bash
# Real-time monitoring
uv run tests/terminal_bench/monitor_evaluation.py

# One-time status check
uv run tests/terminal_bench/monitor_evaluation.py --once
```

### 5. Analyze Results

After completion, generate reports:
```bash
# Find your run directory (e.g., amplifier_train_2025-10-30__14-30-00)
ls -la ai_working/tmp/

# Generate detailed report
uv run tests/terminal_bench/generate_benchmark_report.py \
  --run-dir ai_working/tmp/YOUR_RUN_DIR

# Generate interactive dashboard
uv run tests/terminal_bench/generate_eval_dashboard.py
```

## File Structure

```
tests/terminal_bench/
├── README.md                      # Detailed documentation
├── TERMINAL_BENCH_GUIDE.md        # This guide
├── quick_eval.sh                  # Quick start script
├── run_full_evaluation.py         # Full evaluation runner
├── monitor_evaluation.py          # Real-time progress monitor
├── run_terminal_bench.py          # Legacy runner
├── custom_agents.py               # Agent implementations
├── generate_benchmark_report.py   # Report generator
├── generate_eval_dashboard.py     # Dashboard generator
└── split.json                     # Task splits configuration
```

## Key Scripts Explained

### quick_eval.sh
- **Purpose**: Simplified interface for common evaluation scenarios
- **Best for**: Quick tests and standard evaluations
- **Features**: Auto-cleanup, sensible defaults, clear output

### run_full_evaluation.py
- **Purpose**: Complete control over evaluation parameters
- **Best for**: Custom configurations and experiments
- **Features**: Detailed logging, comparison mode, flexible parameters

### monitor_evaluation.py
- **Purpose**: Track evaluation progress in real-time
- **Best for**: Long-running evaluations
- **Features**: Progress bars, task status, failure tracking

### generate_benchmark_report.py
- **Purpose**: Analyze failures and generate detailed reports
- **Best for**: Understanding failure patterns
- **Features**: AI-powered analysis, failure categorization

## Evaluation Configurations

### Small (Quick Test)
- **Tasks**: 5 tasks
- **Duration**: ~10-15 minutes
- **Purpose**: Verify setup and quick iterations

### Training Set
- **Tasks**: 39 tasks
- **Duration**: ~2-4 hours
- **Purpose**: Main evaluation benchmark

### Test Set
- **Tasks**: 37 tasks
- **Duration**: ~2-4 hours
- **Purpose**: Final validation

### Full (Both Sets)
- **Tasks**: 76 tasks
- **Duration**: ~4-8 hours
- **Purpose**: Complete evaluation

## Performance Optimization

### Concurrent Execution
Adjust based on your system:
```bash
# High-performance system
--concurrent 10

# Standard system (default)
--concurrent 5

# Limited resources
--concurrent 2
```

### Timeout Configuration
For slow tasks or systems:
```bash
# Increase timeouts by 3x
--timeout-multiplier 3.0

# Default (2x)
--timeout-multiplier 2.0
```

## Expected Results

### Success Rates (Typical)
- **Amplifier**: 60-80% on training set
- **Baseline**: 40-60% on training set
- **Improvement**: 15-25% over baseline

### Common Failure Categories
1. **Timeout**: Task exceeds time limit
2. **Test Failure**: Incorrect output or behavior
3. **Setup Issues**: Missing dependencies or configuration
4. **Resource Limits**: Memory or CPU constraints

## Troubleshooting

### Docker Issues
```bash
# Clean up networks
docker network prune -f

# Restart Docker
docker restart

# Check Docker status
docker system df
```

### Memory Issues
```bash
# Reduce concurrent tasks
--concurrent 2

# Monitor memory usage
htop
```

### API Rate Limits
```bash
# Add delays between tasks
--concurrent 1

# Use different API key
export ANTHROPIC_API_KEY="backup-key"
```

## Best Practices

1. **Start Small**: Always test with `--split small` first
2. **Monitor Progress**: Keep monitor running in separate terminal
3. **Save Results**: Results are automatically saved but backup important runs
4. **Clean Docker**: Run `docker network prune -f` between large evaluations
5. **Resource Management**: Adjust concurrency based on system capabilities

## Interpreting Results

### Success Indicators
- High success rate (>70%)
- Consistent performance across task types
- Quick task completion times

### Areas for Investigation
- Tasks with <50% success rate
- Timeout patterns
- Specific failure categories

## Next Steps

After running evaluations:

1. **Analyze Failures**: Use generate_benchmark_report.py
2. **Compare Agents**: Run both amplifier and baseline
3. **Iterate**: Improve agent based on failure patterns
4. **Document**: Record findings and improvements

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review logs in ai_working/tmp/RUN_ID/
3. Examine individual task failures
4. File issues in the Amplifier repository

## Quick Reference Commands

```bash
# Quick test
./tests/terminal_bench/quick_eval.sh

# Full evaluation
./tests/terminal_bench/quick_eval.sh --full

# Monitor progress
uv run tests/terminal_bench/monitor_evaluation.py

# Generate report
uv run tests/terminal_bench/generate_benchmark_report.py --run-dir ai_working/tmp/RUN_ID

# Compare agents
./tests/terminal_bench/quick_eval.sh --both --test
```

---

Ready to run your first evaluation? Start with:
```bash
./tests/terminal_bench/quick_eval.sh
```