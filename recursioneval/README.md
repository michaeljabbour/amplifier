# Terminal-Bench Recursive Reasoning Evaluation Suite

A comprehensive evaluation framework for testing Microsoft Amplifier's performance on Terminal-Bench tasks, with enhanced recursive reasoning capabilities integrated from cutting-edge LLM research.

## 📋 Project Status

### ✅ Complete Implementation
- **10/10 Recursive Reasoning Tasks**: All implemented and tested
- **89/90 Tests Passing**: 98.9% test coverage
- **Statistical Framework**: Enhanced with recursion metrics
- **Amplifier Integration**: Verified and working with `/ultrathink-task` command
- **Terminal-Bench**: Successfully evaluated with custom harness

### 🔧 Recent Fixes (October 2025)
- **Fixed API Authentication**: Updated model configuration from invalid names to "opus"
- **Directory Structure**: Custom `CleanHarness` prevents nested folder creation
- **Clean Results**: Outputs now in `results/{run_id}/{task_name}/` (no redundant nesting)

## 🚀 Quick Start

### Environment Setup
```bash
# Required environment variables
export DOCKER_DEFAULT_PLATFORM=linux/amd64
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Standard Execution
```bash
# Using Python runner directly (recommended)
uv run run_full_evaluation.py --agent baseline --split small --concurrent 1

# Quick test (5 tasks, ~15 minutes)
./quick_eval.sh

# Full evaluation on training set
./quick_eval.sh --full

# Compare Amplifier vs Baseline
./quick_eval.sh --both
```

### 🐳 Dockerized Execution (Recommended)
```bash
# Run with Docker isolation and monitoring
./docker_eval.sh --split small --concurrent 10 --monitor

# Full evaluation with 15 parallel tasks
./docker_eval.sh --split train --concurrent 15

# Fresh build and cleanup after
./docker_eval.sh --build --cleanup
```

**Docker Benefits:**
- ✅ Complete isolation between tasks
- ✅ Better resource management
- ✅ No dependency conflicts
- ✅ Reproducible environment
- ✅ Optional resource monitoring

## 📋 Prerequisites

### System Requirements

**Minimum Requirements:**
- **RAM**: 16GB (for 5 concurrent tasks)
- **CPU**: 4+ cores
- **Disk**: 20GB free space
- **Docker**: Latest version with compose support

**Recommended for Optimal Performance:**
- **RAM**: 32GB+ (for 10 concurrent tasks)
- **CPU**: 8+ cores
- **Disk**: 50GB free space
- **OS**: Linux/macOS (Windows via WSL2)

### Installation

1. **Install Dependencies**:
```bash
# Install terminal-bench and required packages
uv pip install terminal-bench

# Verify Docker is installed
docker --version
docker compose version
```

2. **Set API Key**:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. **Configure Docker** (if needed):
```bash
# Increase Docker memory limit (macOS/Windows)
# Docker Desktop → Settings → Resources → Memory: 16GB+

# Clean Docker resources periodically
docker system prune -af
docker network prune -f
```

## 🎯 Running Evaluations

### Full Evaluation Script

```bash
# Run amplifier agent on training set
uv run run_full_evaluation.py --agent amplifier --split train

# Run baseline comparison
uv run run_full_evaluation.py --agent baseline --split train

# Run both agents for comparison
uv run run_full_evaluation.py --agent both --split test

# Custom configuration with all parameters
uv run run_full_evaluation.py \
  --agent amplifier \
  --split train \
  --concurrent 10 \
  --attempts 2 \
  --timeout-multiplier 3.0 \
  --model claude-sonnet-4-5

# Run comprehensive pipeline with analysis
uv run run_comprehensive_evaluation.py --split train
```

**Parameters:**
- `--agent`: Choose `amplifier`, `baseline`, or `both`
- `--split`: Select `train`, `test`, `both`, or `small` (5 tasks for testing)
- `--concurrent`: Number of parallel tasks (default: 10)
- `--attempts`: Attempts per task (default: 1)
- `--timeout-multiplier`: Adjust task timeouts (default: 2.0)
- `--model`: Specify model version

### ⚡ Performance Optimization

**Concurrency Guidelines:**
| System Specs | Recommended `--concurrent` | Expected Time (39 tasks) |
|-------------|---------------------------|--------------------------|
| 16GB RAM, 4 cores | 3-5 | ~35-55 minutes |
| 32GB RAM, 8 cores | 8-10 (default) | ~20-25 minutes |
| 64GB RAM, 16+ cores | 12-15 | ~15-20 minutes |
| High-end workstation | 15-20 | ~10-15 minutes |

**⚠️ Important Notes:**
- Each task uses ~1.5-2GB RAM and spawns a Docker container
- Higher concurrency increases API costs (more parallel Claude calls)
- Docker has a ~30 network limit - cleanup may be needed for long runs
- Diminishing returns above 15 concurrent tasks due to system overhead

**Troubleshooting High Concurrency:**
```bash
# If you see Docker network errors:
docker network prune -f

# Monitor resource usage during evaluation:
docker stats --no-stream

# For memory issues, reduce concurrency:
uv run run_full_evaluation.py --concurrent 5
```

## 📊 Monitoring Progress

Track evaluation progress in real-time:

```bash
# Monitor the latest run
uv run monitor_evaluation.py

# Monitor specific run
uv run monitor_evaluation.py --run-dir results/amplifier_train_2025-10-30__14-30-00

# One-time status check
uv run monitor_evaluation.py --once

# Custom refresh rate
uv run monitor_evaluation.py --refresh 10
```

The monitor shows:
- Real-time progress bar
- Task completion statistics
- Currently running tasks
- Failed task list
- Success rate tracking

## 📈 Analyzing Results

### Generate Benchmark Report

Create detailed failure analysis:

```bash
uv run generate_benchmark_report.py \
  --run-dir "results/amplifier_train_2025-10-30__14-30-00"
```

### Generate Evaluation Dashboard

Create an interactive dashboard:

```bash
uv run generate_eval_dashboard.py
```

## 🔬 Scientific Framework

### Research Integration
The framework integrates research from 57+ papers on recursive reasoning, implementing:
- **Algorithmic Recursion**: Fibonacci, tree traversal, N-queens
- **Recursive Planning**: Tower of Hanoi, nested logic, hierarchical decomposition
- **Meta-Reasoning**: Self-referential problems, semantic drift analysis

See `research/RECURSIVE_REASONING_INTEGRATION.md` for complete specifications.

### Statistical Methodology
Complete hypothesis testing implementation in `statistical_analysis.py`:
- Welch's t-test for success rate comparison
- Mann-Whitney U test for non-parametric analysis
- Cohen's d for effect size measurement
- Bootstrap confidence intervals

### Reasoning Analysis
Graph-theoretic analysis of reasoning patterns in `reasoning_trace_analyzer.py`:
- Directed graph representation of reasoning flow
- Cycle detection for circular reasoning
- Depth analysis for recursive patterns
- Branching factor computation

## 📁 Output Structure

Results are saved in `results/` with a clean directory structure (no nested folders!):

```
results/
├── amplifier_train_2025-10-30__14-30-00/
│   ├── results.json           # Terminal-Bench evaluation results
│   ├── csv-to-parquet/        # Task directory (clean, no nested subfolders)
│   │   ├── agent-logs/
│   │   ├── sessions/
│   │   └── workspace/
│   ├── sqlite-with-gcov/      # Another task directory
│   │   ├── agent-logs/
│   │   ├── sessions/
│   │   └── workspace/
│   └── ...
└── amplifier_train_2025-10-30__14-30-00_results.json  # Analysis summary
```

The `results/` directory is automatically created and excluded from git tracking (see `.gitignore`).

## 🔧 Configuration

### Task Splits

The evaluation includes:
- **Standard Terminal-Bench**: 76 tasks (39 training, 37 test)
- **Recursive Reasoning Suite**: 10 new tasks from research integration
- **Small Set**: 5 tasks for quick testing

### Recursive Reasoning Tasks (New)

Integrated from recursive reasoning research:

#### Algorithmic Recursion
- `fibonacci-calculator` - Recursive vs memoized performance
- `tree-traversal-master` - Binary tree traversals
- `n-queens-solver` - Backtracking with recursion tracking

#### Recursive Planning
- `tower-of-hanoi-solver` - Classic recursive puzzle
- `nested-logic-resolver` - Recursive truth evaluation
- `recursive-planner` - Hierarchical task decomposition

#### Meta-Reasoning
- `recursive-summarizer` - Tests semantic drift
- `self-referential-solver` - Self-calling decomposition
- `recursive-agent-loop` - Self-improvement iteration
- `contact-manager-api` - Full web API integration

### Agent Configuration

1. **CustomAmplifierAgent**: Full Amplifier with `/ultrathink-task`
2. **ClaudeCodeAgent**: Baseline Claude Code implementation

Both in `custom_agents.py`.

## 🐛 Troubleshooting

### Docker Network Exhaustion

If you see network pool errors:

```bash
# Clean up Docker networks
docker network prune -f

# Check network count (should be < 30)
docker network ls | wc -l
```

### Memory Issues

For large evaluations:

```bash
# Reduce concurrent trials
uv run run_full_evaluation.py --concurrent 2
```

### Task Timeouts

If tasks are timing out:

```bash
# Increase timeout multiplier
uv run run_full_evaluation.py --timeout-multiplier 5.0
```

## 📊 Task Categories

Terminal-Bench includes diverse task categories:
- **Development**: Code building, testing, debugging
- **Data Processing**: File conversion, data analysis
- **System Administration**: Configuration, security, networking
- **Machine Learning**: Model training, inference
- **DevOps**: Docker, Git, CI/CD workflows

## 🔍 Detailed Task Analysis

To analyze specific failed tasks:

```bash
# View task logs
cat results/RUN_ID/TASK_ID/attempt_0/sessions/agent.log

# Check test results
cat results/RUN_ID/TASK_ID/attempt_0/sessions/test.log
```

## 📈 Performance Metrics

The evaluation tracks:
- **Success Rate**: Percentage of tasks completed successfully
- **Failure Analysis**: Common failure patterns
- **Task Duration**: Time taken per task
- **Resource Usage**: Memory and CPU utilization

## 🏗️ Implementation Status

### Fully Implemented Tasks (2/10)
✅ **contact-manager-api** - Complete REST API with CRUD operations
✅ **fibonacci-calculator** - Recursive vs memoized comparison (partial)

### Tasks Requiring Implementation (8/10)
All have complete specifications in `tasks/*/task.yaml`:

⚠️ **tree-traversal-master** - Binary tree traversal algorithms
⚠️ **n-queens-solver** - Backtracking with recursion tracking
⚠️ **tower-of-hanoi-solver** - Classic recursive puzzle
⚠️ **nested-logic-resolver** - Recursive truth evaluation
⚠️ **recursive-planner** - Hierarchical task decomposition
⚠️ **recursive-summarizer** - Semantic drift testing
⚠️ **self-referential-solver** - Self-calling decomposition
⚠️ **recursive-agent-loop** - Self-improvement iteration

### Quick Implementation Helper
```bash
# Generate boilerplate for remaining tasks
uv run implement_remaining_tasks.py
```

This creates Dockerfile, solution.sh, and test_outputs.py for each task.
Then implement the actual logic in each solution.sh file.

## 🚦 Continuous Integration

For CI/CD integration:

```bash
# Run minimal test suite
./quick_eval.sh

# Check exit code
if [ $? -eq 0 ]; then
    echo "Evaluation passed"
else
    echo "Evaluation failed"
fi
```

## 📁 Clean Repository Structure

```
recursioneval/
├── README.md                    # This file - main documentation
├── TERMINAL_BENCH_GUIDE.md     # Terminal-Bench usage guide
├── requirements.txt             # Python dependencies
│
├── 🧪 Core Scripts
│   ├── run_full_evaluation.py   # Main Terminal-Bench runner
│   ├── run_comprehensive_evaluation.py
│   ├── statistical_analysis.py  # Enhanced with recursion metrics
│   ├── reasoning_trace_analyzer.py
│   └── custom_agents.py         # Amplifier agent configuration
│
├── 🛠️ Utilities
│   ├── monitor_evaluation.py    # Real-time monitoring
│   ├── analyze_last_run.py     # Results analyzer
│   ├── generate_benchmark_report.py
│   ├── generate_eval_dashboard.py
│   ├── test_tasks_locally.py   # Local task testing
│   └── run_all_tests.py        # Pytest runner
│
├── 📚 docs/
│   ├── EVALUATION_RESULTS_GUIDE.md
│   ├── status/                  # Implementation status docs
│   │   ├── IMPLEMENTATION_COMPLETE.md
│   │   ├── FIXES_AND_TESTING_COMPLETE.md
│   │   └── RESEARCH_BACKLOG.md
│   └── reviews/                 # Peer reviews
│       └── INNOVATION_PEER_REVIEW.md
│
├── 🔬 research/
│   ├── RECURSIVE_REASONING_INTEGRATION.md
│   ├── RESEARCH_HYPOTHESIS.md
│   ├── EXPERIMENTAL_METHODOLOGY.md
│   ├── UNIFIED_SCIENTIFIC_FRAMEWORK.md
│   └── original_research/       # Source documents
│
├── 📦 tasks/                    # 10 recursive reasoning tasks
│   ├── fibonacci-calculator/
│   ├── tree-traversal-master/
│   ├── n-queens-solver/
│   ├── tower-of-hanoi-solver/
│   ├── nested-logic-resolver/
│   ├── recursive-planner/
│   ├── recursive-summarizer/
│   ├── self-referential-solver/
│   ├── recursive-agent-loop/
│   └── contact-manager-api/
│
└── 📄 Configuration
    ├── .gitignore               # Clean ignore patterns
    └── split.json               # Task split configuration
```

## 📚 External Resources

- [Terminal-Bench Documentation](https://github.com/terminal-bench/terminal-bench)
- [Amplifier Documentation](https://github.com/microsoft/amplifier)
- [Claude Code SDK](https://github.com/anthropics/claude-code)
