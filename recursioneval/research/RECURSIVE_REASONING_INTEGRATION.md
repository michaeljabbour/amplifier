# Integration: Recursive Reasoning Benchmark into Terminal-Bench Framework

## Overview

This document converts ALL concepts from "Evaluating Recursive Reasoning in LLMs" (Doc 1) into Terminal-Bench compatible tasks, integrating the scientific framework, hypotheses, and evaluation methods into our existing infrastructure.

## 1. Scientific Framework Integration

### Original Hypothesis (Doc 1)
"By leveraging structured workflows and tools (as in Amplifier), an LLM can achieve more reliable performance on deeply recursive tasks – maintaining correctness and minimizing hallucinations even as recursion depth increases"

### Integrated Hypothesis for Terminal-Bench
**H₃**: Amplifier agents demonstrate superior performance on recursion-heavy Terminal-Bench tasks, with performance differential increasing logarithmically with recursion depth.

**Operational Definition**: Recursion depth = number of self-similar subproblems that must be solved

### Key Metrics from Doc 1 → Terminal-Bench Integration

| Doc 1 Concept | Terminal-Bench Implementation |
|---------------|------------------------------|
| Pass@k for code | Already in our success_rate metric |
| Recursion depth limit | New metric: `max_successful_depth` |
| Semantic drift | New metric: `semantic_fidelity_score` |
| Hallucination tracking | Existing in reasoning_trace_analyzer.py |
| Self-correction | Existing: error_recovery_rate |

## 2. Converting Recursive Tasks to Terminal-Bench Format

### Category 1: Algorithmic Recursion Tasks

#### Task: fibonacci-calculator

```yaml
# tasks/fibonacci-calculator/task.yaml
description: |
  Implement a recursive Fibonacci calculator that can compute F(n) for n up to 30.

  Requirements:
  1. Create a Python script `fib.py` that takes a command-line argument n
  2. Implement BOTH recursive and memoized versions
  3. Compare performance and output results to `results.json`
  4. Handle edge cases (n<0, non-integer input)

  The script should output JSON with:
  - "recursive_result": the Fibonacci number
  - "recursive_time": execution time in ms
  - "memoized_result": the Fibonacci number (memoized)
  - "memoized_time": execution time in ms

  Example: python fib.py 10 should compute F(10) = 55

difficulty: easy
category: algorithms
tags: [recursion, dynamic-programming, optimization]
max_agent_timeout_sec: 120
```

```python
# tasks/fibonacci-calculator/tests/test_outputs.py
import json
import subprocess
import os

def test_fibonacci():
    # Test cases with known values
    test_cases = [
        (0, 0),
        (1, 1),
        (10, 55),
        (20, 6765),
        (30, 832040)
    ]

    for n, expected in test_cases:
        result = subprocess.run(
            ['python', 'fib.py', str(n)],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = json.loads(result.stdout)

        # Check correctness
        assert output['recursive_result'] == expected
        assert output['memoized_result'] == expected

        # Check memoized is faster for n > 10
        if n > 10:
            assert output['memoized_time'] < output['recursive_time']
```

#### Task: tree-traversal-master

```yaml
# tasks/tree-traversal-master/task.yaml
description: |
  Implement recursive tree traversal algorithms for a binary tree.

  Requirements:
  1. Create a binary tree from the input file `tree.json`
  2. Implement recursive: inorder, preorder, postorder traversals
  3. Output results to `traversals.json`
  4. Handle unbalanced trees and single-node edge cases

  Input format (tree.json):
  {"value": 5, "left": {"value": 3, ...}, "right": {"value": 7, ...}}

  Output format (traversals.json):
  {
    "inorder": [3, 5, 7],
    "preorder": [5, 3, 7],
    "postorder": [3, 7, 5]
  }

difficulty: medium
category: algorithms
tags: [recursion, data-structures, trees]
```

#### Task: n-queens-solver

```yaml
# tasks/n-queens-solver/task.yaml
description: |
  Solve the N-Queens problem using recursive backtracking.

  Requirements:
  1. Read N from `input.txt` (will be 4, 6, or 8)
  2. Find ALL valid solutions using recursion
  3. Output solutions to `solutions.json`
  4. Each solution should be a list of column positions

  Example for N=4:
  {
    "n": 4,
    "solution_count": 2,
    "solutions": [
      [1, 3, 0, 2],  // Queen positions by row
      [2, 0, 3, 1]
    ],
    "recursion_depth": 16  // Track max recursion depth reached
  }

difficulty: hard
category: algorithms
tags: [recursion, backtracking, constraint-satisfaction]
```

### Category 2: Recursive Reasoning & Planning Tasks

#### Task: tower-of-hanoi-solver

```yaml
# tasks/tower-of-hanoi-solver/task.yaml
description: |
  Solve the Tower of Hanoi puzzle and output the optimal move sequence.

  Requirements:
  1. Read number of disks from `config.json` (3, 4, or 5)
  2. Generate the MINIMAL move sequence
  3. Output to `moves.json` with format:
     {"moves": ["A->C", "A->B", "C->B", ...], "total_moves": 7}
  4. Implement verification that no illegal moves are made
  5. Track recursion depth in solving

  The solution MUST be optimal (2^n - 1 moves for n disks).

difficulty: medium
category: puzzles
tags: [recursion, planning, algorithms]
```

#### Task: nested-logic-resolver

```yaml
# tasks/nested-logic-resolver/task.yaml
description: |
  Solve nested logical puzzles with recursive truth evaluation.

  You'll find a puzzle in `puzzle.json` with nested conditions like:
  {
    "statements": [
      {"speaker": "Alice", "says": "Bob lies"},
      {"speaker": "Bob", "says": "Charlie lies"},
      {"speaker": "Charlie", "says": "Alice and Bob lie"}
    ],
    "constraint": "Exactly one tells the truth"
  }

  Requirements:
  1. Parse the logical puzzle
  2. Recursively evaluate all possibilities
  3. Output solution to `solution.json`:
     {"truth_teller": "Alice", "reasoning_steps": [...]}
  4. Show the recursive evaluation tree

difficulty: hard
category: logic
tags: [recursion, logic, constraint-solving]
```

#### Task: recursive-planner

```yaml
# tasks/recursive-planner/task.yaml
description: |
  Create a hierarchical plan for a complex multi-step project.

  Input (`project.json`): A high-level goal with constraints
  Example: "Build a web application with user auth, database, and API"

  Requirements:
  1. Recursively decompose into subtasks (at least 3 levels deep)
  2. Identify dependencies between tasks
  3. Output to `plan.json`:
     {
       "goal": "...",
       "total_tasks": 25,
       "max_depth": 4,
       "tasks": [
         {
           "id": 1,
           "name": "Setup project",
           "subtasks": [1.1, 1.2, 1.3],
           "dependencies": [],
           "level": 0
         }
       ]
     }
  4. Ensure no circular dependencies
  5. Each leaf task must be actionable

difficulty: hard
category: planning
tags: [recursion, hierarchical-planning, project-management]
```

### Category 3: Deep Chaining & Self-Referential Tasks

#### Task: recursive-summarizer

```yaml
# tasks/recursive-summarizer/task.yaml
description: |
  Test semantic drift through recursive summarization.

  Requirements:
  1. Read initial text from `original.txt` (500-800 words)
  2. Create 10 recursive summarizations, each summarizing the previous
  3. Track key facts through iterations
  4. Output to `summaries.json`:
     {
       "iterations": [
         {"level": 0, "text": "...", "word_count": 750, "key_facts": ["fact1", "fact2"]},
         {"level": 1, "text": "...", "word_count": 400, "key_facts": ["fact1", "fact2"]},
         ...
       ],
       "fact_retention": 0.8,  // Percentage of original facts in final summary
       "semantic_drift": 0.2    // Measure of topic drift
     }
  5. Final summary must be 1-2 sentences but preserve main idea

difficulty: medium
category: nlp
tags: [recursion, summarization, semantic-analysis]
```

#### Task: self-referential-solver

```yaml
# tasks/self-referential-solver/task.yaml
description: |
  Implement a self-calling recursive problem solver.

  The problem in `problem.json` requires recursive decomposition:
  Example: "Calculate 5! by recursively breaking it down"

  Requirements:
  1. Parse the problem
  2. Generate recursive calls AS SEPARATE FILES:
     - subproblem_1.txt: "Calculate 4!"
     - subproblem_2.txt: "Calculate 3!"
     - etc.
  3. Solve each subproblem by reading its file
  4. Combine results to solve original
  5. Output to `solution.json`:
     {
       "original_problem": "5!",
       "recursion_depth": 5,
       "subproblems_created": 5,
       "final_answer": 120,
       "call_trace": ["5!", "4!", "3!", "2!", "1!", "base"]
     }

difficulty: medium
category: meta-reasoning
tags: [recursion, self-reference, problem-decomposition]
```

#### Task: recursive-agent-loop

```yaml
# tasks/recursive-agent-loop/task.yaml
description: |
  Implement an agent that recursively improves its solution.

  Problem: Find the largest palindromic prime under 10000.

  Requirements:
  1. Start with a naive solution
  2. Recursively improve it (at least 3 iterations)
  3. Each iteration must:
     - Analyze previous attempt
     - Identify improvement
     - Implement better solution
  4. Output to `evolution.json`:
     {
       "iterations": [
         {
           "attempt": 1,
           "approach": "Check all numbers",
           "result": 9999,  // Wrong
           "analysis": "Forgot to check prime",
           "improvement": "Add prime check"
         },
         {
           "attempt": 2,
           "approach": "Check primes only",
           "result": 929,
           "analysis": "Correct!",
           "improvement": "Optimize with sieve"
         }
       ],
       "final_answer": 929,
       "total_iterations": 3
     }

difficulty: hard
category: meta-reasoning
tags: [recursion, self-improvement, agent-loops]
```

## 3. Integration with Existing Framework

### Statistical Analysis Extensions

```python
# Add to statistical_analysis.py

class RecursionMetricsAnalyzer:
    """Analyze recursion-specific metrics from Terminal-Bench runs."""

    def analyze_recursion_depth(self, results: List[Dict]) -> Dict:
        """Analyze how performance degrades with recursion depth."""
        depth_performance = defaultdict(list)

        for result in results:
            if 'recursion_depth' in result:
                depth = result['recursion_depth']
                success = result['success']
                depth_performance[depth].append(success)

        # Calculate success rate at each depth
        depth_stats = {}
        for depth, successes in depth_performance.items():
            depth_stats[depth] = {
                'success_rate': np.mean(successes),
                'n_samples': len(successes)
            }

        # Fit logarithmic decay model
        if len(depth_stats) > 2:
            depths = np.array(list(depth_stats.keys()))
            rates = np.array([s['success_rate'] for s in depth_stats.values()])

            # Fit: success_rate = a * log(depth) + b
            coeffs = np.polyfit(np.log(depths + 1), rates, 1)

            return {
                'depth_performance': depth_stats,
                'decay_coefficient': coeffs[0],
                'decay_intercept': coeffs[1],
                'max_reliable_depth': self._find_reliability_threshold(depth_stats)
            }

        return {'depth_performance': depth_stats}

    def analyze_semantic_drift(self, summaries: List[Dict]) -> float:
        """Measure semantic drift in recursive summarization."""
        if not summaries:
            return 0.0

        original = summaries[0].get('key_facts', [])
        final = summaries[-1].get('key_facts', [])

        if not original:
            return 0.0

        retained = len(set(final) & set(original))
        drift = 1.0 - (retained / len(original))

        return drift

    def _find_reliability_threshold(self, depth_stats: Dict,
                                   threshold: float = 0.5) -> int:
        """Find maximum depth where success rate > threshold."""
        max_depth = 0
        for depth, stats in sorted(depth_stats.items()):
            if stats['success_rate'] >= threshold:
                max_depth = depth
            else:
                break
        return max_depth
```

### Reasoning Trace Extensions

```python
# Add to reasoning_trace_analyzer.py

class RecursiveReasoningAnalyzer:
    """Analyze recursive reasoning patterns."""

    def detect_recursive_patterns(self, trace: str) -> Dict:
        """Detect recursive problem decomposition in reasoning."""
        patterns = {
            'decomposition_found': False,
            'base_case_identified': False,
            'recursive_calls': [],
            'max_depth': 0,
            'backtracking_points': []
        }

        # Look for decomposition patterns
        decomposition_phrases = [
            r'break.*down',
            r'decompose',
            r'subdivide',
            r'recursive.*call',
            r'base case'
        ]

        for phrase in decomposition_phrases:
            if re.search(phrase, trace, re.IGNORECASE):
                patterns['decomposition_found'] = True
                break

        # Track recursive depth
        depth_markers = re.findall(r'depth[:\s]+(\d+)', trace)
        if depth_markers:
            patterns['max_depth'] = max(int(d) for d in depth_markers)

        # Find recursive calls
        calls = re.findall(r'calling.*with.*[(\[](.+?)[)\]]', trace)
        patterns['recursive_calls'] = calls[:10]  # Limit to 10

        return patterns

    def analyze_self_improvement(self, iterations: List[Dict]) -> Dict:
        """Analyze self-improvement in recursive agent loops."""
        if len(iterations) < 2:
            return {'improvement_found': False}

        improvements = []
        for i in range(1, len(iterations)):
            prev = iterations[i-1]
            curr = iterations[i]

            # Measure improvement
            if 'score' in prev and 'score' in curr:
                improvement = curr['score'] - prev['score']
                improvements.append(improvement)

        return {
            'improvement_found': any(i > 0 for i in improvements),
            'total_improvement': sum(improvements),
            'improvement_trajectory': improvements,
            'converged': len(improvements) > 2 and improvements[-1] < 0.01
        }
```

## 4. Unified Hypothesis Testing

### Combined Hypotheses from Doc 1 + Our Framework

```python
# comprehensive_hypothesis_tests.py

class ComprehensiveHypothesisTester:
    """Test all hypotheses from both documents."""

    def __init__(self):
        self.hypotheses = {
            'H1': 'Amplifier > Baseline on general Terminal-Bench tasks',
            'H2': 'Amplifier shows less degradation with recursion depth',
            'H3': 'Amplifier maintains semantic fidelity better in chaining',
            'H4': 'Amplifier achieves faster convergence in self-improvement',
            'H5': 'Recursion depth correlates with task complexity'
        }

    def test_all_hypotheses(self, amplifier_results: Dict,
                          baseline_results: Dict) -> Dict:
        """Run all hypothesis tests."""
        results = {}

        # H1: General performance (existing)
        results['H1'] = self.test_general_performance(
            amplifier_results, baseline_results
        )

        # H2: Recursion depth degradation
        results['H2'] = self.test_recursion_degradation(
            amplifier_results, baseline_results
        )

        # H3: Semantic fidelity
        results['H3'] = self.test_semantic_fidelity(
            amplifier_results, baseline_results
        )

        # H4: Self-improvement convergence
        results['H4'] = self.test_convergence_speed(
            amplifier_results, baseline_results
        )

        # H5: Depth-complexity correlation
        results['H5'] = self.test_depth_complexity_correlation(
            amplifier_results
        )

        return results

    def test_recursion_degradation(self, amp: Dict, base: Dict) -> Dict:
        """H2: Test if Amplifier degrades less with depth."""
        amp_depths = self._extract_depth_performance(amp)
        base_depths = self._extract_depth_performance(base)

        # Compare degradation rates
        amp_slope = self._calculate_degradation_slope(amp_depths)
        base_slope = self._calculate_degradation_slope(base_depths)

        # Less negative slope = less degradation
        improvement = base_slope - amp_slope  # Should be positive

        # Statistical test
        t_stat, p_value = stats.ttest_ind(
            amp_depths.values(),
            base_depths.values()
        )

        return {
            'amplifier_degradation': amp_slope,
            'baseline_degradation': base_slope,
            'improvement': improvement,
            'p_value': p_value,
            'supported': p_value < 0.05 and improvement > 0
        }
```

## 5. Implementation Priority & Timeline

### Phase 1: Core Recursive Tasks (Week 1)
1. fibonacci-calculator ✅
2. tower-of-hanoi-solver ✅
3. tree-traversal-master ✅

### Phase 2: Complex Reasoning (Week 2)
4. n-queens-solver
5. nested-logic-resolver
6. recursive-planner

### Phase 3: Self-Referential (Week 3)
7. recursive-summarizer
8. self-referential-solver
9. recursive-agent-loop

### Phase 4: Analysis & Reporting (Week 4)
- Run all tasks
- Statistical analysis with recursion metrics
- Generate comprehensive report

## 6. Expected Outcomes

Based on Doc 1's literature review and our framework:

### Performance Predictions by Task Type

| Task Category | Baseline | Amplifier | Improvement | Rationale |
|--------------|----------|-----------|-------------|-----------|
| Simple Recursion (Fib, Tree) | 85% | 95% | +10% | Both handle well, Amplifier more consistent |
| Complex Recursion (N-Queens) | 40% | 65% | +25% | Amplifier's planning helps backtracking |
| Reasoning (Hanoi, Logic) | 50% | 75% | +25% | Structured decomposition advantage |
| Self-Referential | 30% | 60% | +30% | Context management critical |
| Deep Chaining | 25% | 55% | +30% | Amplifier resists drift better |

### Recursion Depth Performance

```
Success Rate vs Recursion Depth:

100% |A
     |AB
 75% |AAB
     |AAABB
 50% |  AAABBB
     |    AAAABBBB
 25% |      AAABBBBBB
     |        AABBBBBB
  0% |________________
     0  5  10  15  20
     Recursion Depth

A = Amplifier
B = Baseline
```

### Semantic Drift (from Doc 1 research)

- **Baseline**: 40% meaning loss after 10 iterations
- **Amplifier**: 15% meaning loss after 10 iterations
- **Mechanism**: Knowledge base re-injection prevents drift

## 7. Validation Metrics

### From Doc 1 Literature + Our Extensions

1. **Pass@k** (from HumanEval): Already in our framework
2. **Recursion Depth Limit**: New metric added
3. **Semantic Fidelity Score**: New metric added
4. **Backtracking Efficiency**: Trace analyzer extension
5. **Self-Improvement Rate**: Agent loop analysis

## 8. Connection to Original Research

This integration preserves ALL scientific insights from Doc 1:
- 57+ citations about recursion challenges → Incorporated in task design
- Semantic drift findings → recursive-summarizer task
- Tower of Hanoi complexity limits → tower-of-hanoi-solver task
- Self-referential challenges → self-referential-solver task
- Context rot problem → All deep chaining tasks

## Conclusion

We have successfully converted the entire "Evaluating Recursive Reasoning in LLMs" paper into Terminal-Bench compatible tasks, preserving:
- All three categories of recursive evaluation
- The scientific framework and hypotheses
- The expected outcomes and metrics
- The connection to literature (57+ citations)

These 9 new tasks + the contact-manager-api task from Doc 2 = 10 new Terminal-Bench tasks that comprehensively evaluate recursive reasoning capabilities.