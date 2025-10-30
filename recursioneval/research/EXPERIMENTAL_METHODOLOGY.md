# Terminal-Bench Experimental Methodology

## Table of Contents
1. [Experimental Framework](#experimental-framework)
2. [Implementation Architecture](#implementation-architecture)
3. [Test Suite Detailed Analysis](#test-suite-detailed-analysis)
4. [Measurement Protocols](#measurement-protocols)
5. [Statistical Validation](#statistical-validation)
6. [Quality Assurance](#quality-assurance)

## 1. Experimental Framework

### 1.1 Scientific Method Application

Our experimental approach follows the classical scientific method:

1. **Observation**: LLMs struggle with complex, multi-step terminal tasks
2. **Question**: Can recursive reasoning enhancement improve performance?
3. **Hypothesis**: Amplifier's structured thinking improves task completion
4. **Experiment**: Terminal-Bench comparative evaluation
5. **Analysis**: Statistical comparison of success rates
6. **Conclusion**: Evidence-based assessment of enhancement value

### 1.2 Experimental Controls

#### Independent Variable Manipulation
- **Control Group**: Baseline Claude Code Agent
  - Standard tool access (Bash, Edit, Write, Read, etc.)
  - No specialized reasoning commands
  - Direct instruction processing

- **Treatment Group**: Amplifier-Enhanced Agent
  - Same base tools as control
  - Additional `/ultrathink-task` command
  - Structured reasoning framework

#### Confounding Variable Control
- **Model Consistency**: Same base model (Claude-3.5-Sonnet)
- **Environment Isolation**: Docker containers for each task
- **Resource Allocation**: Identical CPU/memory limits
- **Timeout Standardization**: 2x base timeout for both agents
- **Randomization**: Task order randomized to prevent learning effects

## 2. Implementation Architecture

### 2.1 System Components

```
recursioneval/
├── Core Evaluation Engine
│   ├── run_full_evaluation.py    # Main orchestrator
│   ├── custom_agents.py          # Agent implementations
│   └── split.json                # Task distribution
│
├── Monitoring & Analysis
│   ├── monitor_evaluation.py     # Real-time tracking
│   ├── generate_benchmark_report.py  # Failure analysis
│   └── generate_eval_dashboard.py    # Visualization
│
├── Utilities
│   ├── quick_eval.sh            # Simplified launcher
│   └── test_single_task.py      # Unit testing
│
└── Documentation
    ├── README.md                 # User guide
    ├── RESEARCH_HYPOTHESIS.md    # Scientific framework
    └── EXPERIMENTAL_METHODOLOGY.md  # This document
```

### 2.2 Agent Architecture

#### CustomAmplifierAgent
```python
class CustomAmplifierAgent(AbstractInstalledAgent):
    # Key differentiation: /ultrathink-task preprocessing
    def _run_agent_commands(self, instruction: str):
        instruction = f"/ultrathink-task {instruction}"  # Enhancement
        return execute_with_tools(instruction)
```

**Reasoning Enhancement Pipeline**:
1. Receive task instruction
2. Invoke `/ultrathink-task` for structured analysis
3. Generate decomposed subtask graph
4. Execute subtasks with state management
5. Synthesize results

#### ClaudeCodeAgent (Baseline)
```python
class ClaudeCodeAgent(AbstractInstalledAgent):
    # Direct execution without preprocessing
    def _run_agent_commands(self, instruction: str):
        return execute_with_tools(instruction)  # No enhancement
```

**Standard Execution Pipeline**:
1. Receive task instruction
2. Direct interpretation and planning
3. Sequential tool execution
4. Result compilation

### 2.3 Docker Containerization

Each task runs in an isolated Docker container:

```dockerfile
# Implicit Dockerfile behavior
FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl git make build-essential
# Agent-specific installation
COPY agent_script.sh /install.sh
RUN /install.sh
WORKDIR /workspace
```

**Isolation Benefits**:
- Prevents cross-task contamination
- Ensures reproducibility
- Standardizes environment
- Enables parallel execution

## 3. Test Suite Detailed Analysis

### 3.1 Training Set Tasks (39 tasks)

#### Data Processing Tasks
| Task ID | Description | Complexity | Recursive Depth | Key Challenges |
|---------|-------------|------------|-----------------|----------------|
| csv-to-parquet | Convert CSV files to Parquet format | Low | 1 | Schema inference, data type handling |
| heterogeneous-dates | Parse mixed date formats | Medium | 2 | Pattern recognition, error handling |
| reshard-c4-data | Reorganize large dataset | High | 3 | Memory management, parallel processing |
| count-dataset-tokens | Token counting in datasets | Medium | 2 | Tokenizer selection, batch processing |

#### Development Tasks
| Task ID | Description | Complexity | Recursive Depth | Key Challenges |
|---------|-------------|------------|-----------------|----------------|
| pytorch-model-cli | Create CLI for PyTorch model | High | 4 | Argument parsing, model loading |
| swe-bench-fsspec | Fix filesystem spec issue | High | 5 | Code understanding, debugging |
| swe-bench-astropy-2 | Astronomy package bug fix | High | 5 | Domain knowledge, testing |
| modernize-fortran-build | Update Fortran build system | Medium | 3 | Legacy code, build tools |

#### Security Tasks
| Task ID | Description | Complexity | Recursive Depth | Key Challenges |
|---------|-------------|------------|-----------------|----------------|
| crack-7z-hash | Password recovery for 7z | Medium | 3 | Tool selection, brute force |
| security-vulhub-minio | Exploit Minio vulnerability | High | 4 | Security knowledge, exploitation |
| password-recovery | General password recovery | Medium | 3 | Multiple formats, tools |
| intrusion-detection | Setup IDS system | High | 5 | Configuration, rule writing |

#### System Administration
| Task ID | Description | Complexity | Recursive Depth | Key Challenges |
|---------|-------------|------------|-----------------|----------------|
| nginx-request-logging | Configure Nginx logging | Medium | 2 | Config syntax, log formats |
| configure-git-webserver | Setup Git HTTP server | Medium | 3 | Apache/Nginx config, permissions |
| jupyter-notebook-server | Deploy Jupyter server | Medium | 3 | Security, configuration |
| tmux-advanced-workflow | Complex tmux setup | High | 4 | Session management, scripting |

### 3.2 Test Set Tasks (37 tasks)

#### Algorithm Implementation
| Task ID | Description | Complexity | Recursive Depth | Key Challenges |
|---------|-------------|------------|-----------------|----------------|
| blind-maze-explorer | Maze solving algorithm | High | 6 | Pathfinding, state management |
| grid-pattern-transform | 2D grid transformations | Medium | 3 | Pattern matching, algorithms |
| fibonacci-server | Fibonacci API server | Low | 2 | Server setup, algorithm |
| path-tracing | Ray tracing implementation | High | 5 | Graphics algorithms, optimization |

#### Build System Tasks
| Task ID | Description | Complexity | Recursive Depth | Key Challenges |
|---------|-------------|------------|-----------------|----------------|
| build-tcc-qemu | Build TCC in QEMU | High | 5 | Cross-compilation, emulation |
| build-initramfs-qemu | Create initramfs | High | 4 | Kernel, boot process |
| qemu-alpine-ssh | Setup Alpine in QEMU | Medium | 3 | Virtualization, networking |
| polyglot-rust-c | Multi-language project | High | 4 | Build systems, FFI |

### 3.3 Task Complexity Scoring

Each task is scored on multiple dimensions:

```python
complexity_score = (
    step_count * 0.3 +          # Number of operations
    branch_factor * 0.2 +        # Decision points
    state_complexity * 0.2 +     # Context management
    tool_diversity * 0.15 +      # Different tools needed
    error_likelihood * 0.15      # Failure probability
)
```

## 4. Measurement Protocols

### 4.1 Primary Metrics

#### Success Rate
```python
success_rate = successful_tasks / total_tasks * 100
```
- **Binary Classification**: Task passes all tests or fails
- **No Partial Credit**: Ensures clear performance signal

#### Time to Completion
```python
time_metrics = {
    'mean': np.mean(completion_times),
    'median': np.median(completion_times),
    'std': np.std(completion_times),
    'p95': np.percentile(completion_times, 95)
}
```

#### Error Recovery Rate
```python
recovery_rate = tasks_succeeded_after_error / tasks_with_errors * 100
```

### 4.2 Secondary Metrics

#### Tool Usage Patterns
- Frequency of each tool usage
- Tool sequences and patterns
- Error-to-tool correlations

#### Reasoning Depth
- Number of subtasks generated
- Recursion levels reached
- Backtracking frequency

### 4.3 Data Collection

All metrics are automatically collected via:

1. **Agent Logs** (`agent.log`):
   - Complete interaction transcript
   - Tool invocations
   - Reasoning traces

2. **Test Logs** (`test.log`):
   - Test execution output
   - Success/failure determination
   - Error messages

3. **Metadata** (`results.json`):
   - Timing information
   - Resource usage
   - Task configuration

## 5. Statistical Validation

### 5.1 Sample Size Calculation

Using power analysis for two-sample t-test:

```python
from statsmodels.stats.power import tt_solve_power

effect_size = 0.5  # Medium effect (Cohen's d)
alpha = 0.05       # Significance level
power = 0.80       # Statistical power

n = tt_solve_power(effect_size=effect_size,
                   alpha=alpha,
                   power=power)
# Result: n ≈ 64 per group
```

With 76 total tasks, we have sufficient power to detect medium effects.

### 5.2 Statistical Tests

#### Primary Analysis: Two-Sample T-Test
```python
from scipy import stats

t_stat, p_value = stats.ttest_ind(
    amplifier_scores,
    baseline_scores,
    equal_var=False  # Welch's t-test
)

confidence_interval = stats.t.interval(
    0.95,
    df=len(amplifier_scores) - 1,
    loc=np.mean(amplifier_scores),
    scale=stats.sem(amplifier_scores)
)
```

#### Assumptions Validation
1. **Independence**: Tasks run in isolation
2. **Normality**: Shapiro-Wilk test (p > 0.05)
3. **Homogeneity**: Levene's test for variance

#### Non-Parametric Alternative: Mann-Whitney U
```python
u_stat, p_value = stats.mannwhitneyu(
    amplifier_scores,
    baseline_scores,
    alternative='two-sided'
)
```

### 5.3 Effect Size Calculation

```python
def cohen_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

effect_size = cohen_d(amplifier_scores, baseline_scores)
# Interpretation:
# 0.2 = small, 0.5 = medium, 0.8 = large
```

## 6. Quality Assurance

### 6.1 Validation Protocols

#### Pre-Execution Validation
- [ ] API key configuration
- [ ] Docker daemon status
- [ ] Disk space availability
- [ ] Network connectivity
- [ ] Dependency installation

#### During Execution
- [ ] Container health monitoring
- [ ] Resource usage tracking
- [ ] Timeout enforcement
- [ ] Error logging
- [ ] Progress tracking

#### Post-Execution Validation
- [ ] Data completeness check
- [ ] Log file integrity
- [ ] Result consistency
- [ ] Statistical assumptions
- [ ] Outlier detection

### 6.2 Error Handling Matrix

| Error Type | Detection | Mitigation | Recovery |
|------------|-----------|------------|----------|
| Docker Network Exhaustion | Network count > 30 | Auto-cleanup | Retry task |
| API Rate Limit | 429 response | Exponential backoff | Queue delay |
| Container Crash | Exit code != 0 | Resource increase | Restart container |
| Timeout | Duration > limit | Kill process | Mark as failed |
| Disk Full | Write error | Space cleanup | Resume from checkpoint |

### 6.3 Data Integrity

#### Checksums and Validation
```python
def validate_results(results_file):
    data = json.load(results_file)

    # Check required fields
    assert 'results' in data
    assert 'metadata' in data

    # Validate each result
    for result in data['results']:
        assert 'task_id' in result
        assert 'success' in result
        assert isinstance(result['success'], bool)

    # Check consistency
    assert len(data['results']) == data['metadata']['total_tasks']

    return True
```

## 7. Reproducibility Checklist

### 7.1 Environment Specification

```yaml
System Requirements:
  OS: Ubuntu 20.04+ / macOS 12+
  Python: 3.10+
  Docker: 20.10+
  Memory: 16GB minimum
  Storage: 50GB available

Dependencies:
  - terminal-bench==0.2.18
  - anthropic
  - docker
  - pandas
  - numpy

Environment Variables:
  - ANTHROPIC_API_KEY
  - ANTHROPIC_MODEL (optional)
```

### 7.2 Execution Steps

1. **Setup**:
```bash
git clone https://github.com/microsoft/amplifier
cd amplifier/recursioneval
uv pip install terminal-bench
export ANTHROPIC_API_KEY="your-key"
```

2. **Validation**:
```bash
./quick_eval.sh --help
docker --version
```

3. **Execution**:
```bash
# Test run
./quick_eval.sh

# Full evaluation
./quick_eval.sh --full --both
```

4. **Analysis**:
```bash
uv run generate_benchmark_report.py --run-dir ai_working/tmp/RUN_ID
```

### 7.3 Random Seed Control

```python
# Set seeds for reproducibility
import random
import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Task ordering
task_ids = split_data["train"]
random.shuffle(task_ids)  # Consistent shuffle
```

## 8. Peer Review Guidelines

### 8.1 Review Criteria

Reviewers should evaluate:

1. **Hypothesis Clarity**: Is the research question well-defined?
2. **Methodology Soundness**: Are controls adequate?
3. **Statistical Rigor**: Are tests appropriate?
4. **Code Quality**: Is implementation correct?
5. **Reproducibility**: Can results be replicated?
6. **Documentation**: Is methodology clear?

### 8.2 Review Checklist

- [ ] Hypothesis is testable and specific
- [ ] Control and treatment groups properly defined
- [ ] Sample size adequate for statistical power
- [ ] Confounding variables controlled
- [ ] Measurement protocols standardized
- [ ] Statistical tests appropriate
- [ ] Code is functional and documented
- [ ] Results are reproducible
- [ ] Limitations acknowledged
- [ ] Conclusions supported by data

## 9. Ethical Considerations

### 9.1 Resource Usage
- API calls are metered and costly
- Implement rate limiting
- Use minimal viable sample sizes
- Cache results when possible

### 9.2 Transparency
- All code open source
- Methods fully documented
- Failures reported honestly
- Limitations acknowledged

### 9.3 Bias Mitigation
- Diverse task selection
- Multiple domains tested
- Both simple and complex tasks
- No cherry-picking results

---

*This document represents a comprehensive methodology for scientific evaluation of LLM recursive reasoning capabilities using Terminal-Bench.*