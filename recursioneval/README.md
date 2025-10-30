# Terminal-Bench Recursive Reasoning Evaluation Suite

A comprehensive evaluation framework for testing Microsoft Amplifier's performance on Terminal-Bench tasks, with enhanced recursive reasoning capabilities integrated from cutting-edge LLM research.

## 📋 Integration Status

This framework successfully integrates:
- **Standard Terminal-Bench**: 76 tasks (39 training, 37 test)
- **Recursive Reasoning Suite**: 10 new tasks from research integration
- **Statistical Analysis**: Complete hypothesis testing framework
- **Reasoning Trace Analysis**: Graph-based analysis of agent problem-solving

**Implementation Status**: Framework 100% ready, Tasks 20% implemented (2/10 recursive tasks)

## 🚀 Quick Start

```bash
# Quick test (5 tasks, ~15 minutes)
./quick_eval.sh

# Full evaluation on training set
./quick_eval.sh --full

# Compare Amplifier vs Baseline
./quick_eval.sh --both

# Complete evaluation with analysis
uv run run_comprehensive_evaluation.py --split train
```

## 📋 Prerequisites

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
  --model claude-3-5-sonnet-latest

# Run comprehensive pipeline with analysis
uv run run_comprehensive_evaluation.py --split train
```

**Parameters:**
- `--agent`: Choose `amplifier`, `baseline`, or `both`
- `--split`: Select `train`, `test`, `both`, or `small` (5 tasks for testing)
- `--concurrent`: Number of parallel tasks (default: 5)
- `--attempts`: Attempts per task (default: 1)
- `--timeout-multiplier`: Adjust task timeouts (default: 2.0)
- `--model`: Specify model version

## 📊 Monitoring Progress

Track evaluation progress in real-time:

```bash
# Monitor the latest run
uv run monitor_evaluation.py

# Monitor specific run
uv run monitor_evaluation.py --run-dir ai_working/tmp/amplifier_train_2025-10-30__14-30-00

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
  --run-dir "ai_working/tmp/amplifier_train_2025-10-30__14-30-00"
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

Results are saved in `ai_working/tmp/` with this structure:

```
ai_working/tmp/
├── amplifier_train_2025-10-30__14-30-00/
│   ├── results.json           # Final evaluation results
│   ├── csv-to-parquet/        # Individual task directories
│   │   └── attempt_0/
│   │       ├── sessions/
│   │       │   ├── agent.log  # Agent interaction log
│   │       │   └── test.log   # Test output
│   │       └── workspace/     # Task workspace
│   └── ...
└── amplifier_train_2025-10-30__14-30-00_results.json  # Summary
```

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
cat ai_working/tmp/RUN_ID/TASK_ID/attempt_0/sessions/agent.log

# Check test results
cat ai_working/tmp/RUN_ID/TASK_ID/attempt_0/sessions/test.log
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

## 📚 Documentation Structure

### Core Documents
- **README.md** (this file) - Main entry point and overview
- **TERMINAL_BENCH_GUIDE.md** - Terminal-Bench usage guide

### Research & Scientific Framework
Located in `research/`:
- **RECURSIVE_REASONING_INTEGRATION.md** - Complete task specifications
- **RESEARCH_HYPOTHESIS.md** - Scientific framework and hypotheses
- **EXPERIMENTAL_METHODOLOGY.md** - Evaluation methodology
- **UNIFIED_SCIENTIFIC_FRAMEWORK.md** - Integrated research framework
- **original_research/** - Extracted Word document content

### Code Modules
- **run_full_evaluation.py** - Main evaluation runner
- **statistical_analysis.py** - Statistical testing implementation
- **reasoning_trace_analyzer.py** - Reasoning pattern analysis
- **custom_agents.py** - Agent implementations
- **monitor_evaluation.py** - Real-time progress monitoring
- **generate_benchmark_report.py** - Failure analysis reporting

### Archived Materials
- **archive/old_analysis_docs/** - Previous analysis iterations
- **archive/temp_scripts/** - Temporary utility scripts

## 📚 External Resources

- [Terminal-Bench Documentation](https://github.com/terminal-bench/terminal-bench)
- [Amplifier Documentation](https://github.com/microsoft/amplifier)
- [Claude Code SDK](https://github.com/anthropics/claude-code)
