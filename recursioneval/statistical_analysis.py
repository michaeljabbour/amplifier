#!/usr/bin/env python3
"""
Statistical Analysis Module for Terminal-Bench Evaluation

This module implements comprehensive statistical analysis for comparing
Amplifier vs Baseline agent performance on Terminal-Bench tasks.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    import scipy.stats as stats
    from scipy.stats import bootstrap
except ImportError:
    print("Warning: scipy not installed. Install with: pip install scipy")
    stats = None


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    task_id: str
    agent: str
    success: bool
    time_taken: float
    tokens_used: int
    tool_calls: int
    errors: int
    backtracks: int
    recursion_depth: Optional[int] = None
    recursion_data: Optional[Dict[str, Any]] = None


class RecursionMetricsAnalyzer:
    """Analyzes recursion-specific performance metrics.

    Tracks how effectively agents handle recursive problem decomposition,
    measuring depth achieved, degradation patterns, and branching consistency.
    """

    def __init__(self, results: List[EvaluationResult]):
        """Initialize with evaluation results containing recursion data."""
        self.results = [r for r in results if r.recursion_data is not None]

    def analyze_max_depth_achieved(self) -> Dict[str, Any]:
        """Track maximum recursion depth achieved per task.

        Returns:
            Dict containing depth statistics and per-task breakdown
        """
        depths = [r.recursion_depth for r in self.results if r.recursion_depth is not None]

        if not depths:
            return {'error': 'No recursion depth data available'}

        return {
            'mean_depth': np.mean(depths),
            'median_depth': np.median(depths),
            'max_depth': np.max(depths),
            'min_depth': np.min(depths),
            'std_depth': np.std(depths),
            'depth_distribution': {
                'shallow (1-2)': sum(1 for d in depths if d <= 2),
                'medium (3-5)': sum(1 for d in depths if 3 <= d <= 5),
                'deep (6+)': sum(1 for d in depths if d >= 6)
            }
        }

    def analyze_depth_degradation_curves(self) -> Dict[str, Any]:
        """Analyze how solution quality degrades with recursion depth.

        Returns:
            Dict containing degradation metrics per depth level
        """
        depth_to_success = {}

        for result in self.results:
            if result.recursion_depth is None:
                continue
            depth = result.recursion_depth
            if depth not in depth_to_success:
                depth_to_success[depth] = {'successes': 0, 'total': 0}
            depth_to_success[depth]['total'] += 1
            if result.success:
                depth_to_success[depth]['successes'] += 1

        degradation_curve = {}
        for depth, counts in sorted(depth_to_success.items()):
            success_rate = counts['successes'] / counts['total'] if counts['total'] > 0 else 0
            degradation_curve[f'depth_{depth}'] = {
                'success_rate': success_rate * 100,
                'n_tasks': counts['total']
            }

        return {
            'curve': degradation_curve,
            'degradation_detected': self._detect_degradation_trend(degradation_curve)
        }

    def _detect_degradation_trend(self, curve: Dict) -> bool:
        """Detect if there's a clear degradation trend with depth."""
        if len(curve) < 2:
            return False
        rates = [v['success_rate'] for v in curve.values()]
        # Simple check: if success rate decreases monotonically
        return all(rates[i] >= rates[i+1] for i in range(len(rates)-1))

    def analyze_stack_efficiency(self) -> Dict[str, Any]:
        """Measure efficiency of recursion stack usage.

        Returns:
            Dict containing stack efficiency metrics
        """
        efficiency_metrics = []

        for result in self.results:
            if not result.recursion_data:
                continue

            # Calculate efficiency as success per depth unit
            if result.recursion_depth and result.recursion_depth > 0:
                efficiency = result.success / result.recursion_depth
                efficiency_metrics.append({
                    'task_id': result.task_id,
                    'efficiency': efficiency,
                    'depth': result.recursion_depth,
                    'success': result.success
                })

        if not efficiency_metrics:
            return {'error': 'No stack efficiency data available'}

        efficiencies = [m['efficiency'] for m in efficiency_metrics]

        return {
            'mean_efficiency': np.mean(efficiencies),
            'median_efficiency': np.median(efficiencies),
            'efficiency_by_depth': self._efficiency_by_depth(efficiency_metrics)
        }

    def _efficiency_by_depth(self, metrics: List[Dict]) -> Dict:
        """Calculate average efficiency grouped by depth."""
        depth_groups = {}
        for m in metrics:
            depth = m['depth']
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(m['efficiency'])

        return {f'depth_{d}': np.mean(effs) for d, effs in sorted(depth_groups.items())}

    def analyze_branching_consistency(self) -> Dict[str, Any]:
        """Analyze consistency of branching decisions across recursion levels.

        Returns:
            Dict containing branching pattern metrics
        """
        branching_data = []

        for result in self.results:
            if not result.recursion_data or 'branches' not in result.recursion_data:
                continue

            branches = result.recursion_data['branches']
            branching_data.append({
                'task_id': result.task_id,
                'branch_count': len(branches),
                'branch_variance': np.var([b.get('depth', 0) for b in branches]) if branches else 0
            })

        if not branching_data:
            return {'error': 'No branching data available'}

        branch_counts = [b['branch_count'] for b in branching_data]
        branch_variances = [b['branch_variance'] for b in branching_data]

        return {
            'mean_branches': np.mean(branch_counts),
            'median_branches': np.median(branch_counts),
            'branch_consistency_score': 1.0 / (1.0 + np.mean(branch_variances)),
            'branching_variance': np.mean(branch_variances)
        }


class SemanticDriftAnalyzer:
    """Analyzes semantic drift in recursive problem decomposition.

    Tracks how well agents maintain semantic fidelity to the original
    problem as they recurse deeper into subproblems.
    """

    def __init__(self, results: List[EvaluationResult]):
        """Initialize with evaluation results containing recursion data."""
        self.results = [r for r in results if r.recursion_data is not None]

    def calculate_fact_retention_score(self) -> Dict[str, Any]:
        """Calculate how well key facts are retained across recursion levels.

        Returns:
            Dict containing retention scores and metrics
        """
        retention_scores = []

        for result in self.results:
            if not result.recursion_data or 'fact_retention' not in result.recursion_data:
                continue

            retention = result.recursion_data['fact_retention']
            retention_scores.append({
                'task_id': result.task_id,
                'retention_score': retention,
                'depth': result.recursion_depth
            })

        if not retention_scores:
            return {'error': 'No fact retention data available'}

        scores = [r['retention_score'] for r in retention_scores]

        return {
            'mean_retention': np.mean(scores),
            'median_retention': np.median(scores),
            'min_retention': np.min(scores),
            'retention_by_depth': self._retention_by_depth(retention_scores)
        }

    def _retention_by_depth(self, scores: List[Dict]) -> Dict:
        """Calculate retention scores grouped by depth."""
        depth_groups = {}
        for s in scores:
            depth = s['depth']
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(s['retention_score'])

        return {f'depth_{d}': np.mean(rets) for d, rets in sorted(depth_groups.items())}

    def track_information_loss_per_depth(self) -> Dict[str, Any]:
        """Track cumulative information loss as recursion depth increases.

        Returns:
            Dict containing information loss metrics
        """
        loss_data = []

        for result in self.results:
            if not result.recursion_data or 'information_loss' not in result.recursion_data:
                continue

            loss = result.recursion_data['information_loss']
            loss_data.append({
                'task_id': result.task_id,
                'information_loss': loss,
                'depth': result.recursion_depth
            })

        if not loss_data:
            return {'error': 'No information loss data available'}

        losses = [l['information_loss'] for l in loss_data]

        return {
            'mean_loss': np.mean(losses),
            'median_loss': np.median(losses),
            'max_loss': np.max(losses),
            'loss_by_depth': self._loss_by_depth(loss_data),
            'loss_acceleration': self._calculate_loss_acceleration(loss_data)
        }

    def _loss_by_depth(self, data: List[Dict]) -> Dict:
        """Calculate information loss grouped by depth."""
        depth_groups = {}
        for d in data:
            depth = d['depth']
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(d['information_loss'])

        return {f'depth_{d}': np.mean(losses) for d, losses in sorted(depth_groups.items())}

    def _calculate_loss_acceleration(self, data: List[Dict]) -> float:
        """Calculate if information loss accelerates with depth."""
        loss_by_depth = self._loss_by_depth(data)
        if len(loss_by_depth) < 2:
            return 0.0

        losses = [v for v in loss_by_depth.values()]
        # Calculate rate of change
        deltas = [losses[i+1] - losses[i] for i in range(len(losses)-1)]
        return np.mean(deltas) if deltas else 0.0

    def calculate_semantic_fidelity_metrics(self) -> Dict[str, Any]:
        """Calculate overall semantic fidelity across all recursion levels.

        Returns:
            Dict containing comprehensive semantic fidelity metrics
        """
        fidelity_scores = []

        for result in self.results:
            if not result.recursion_data or 'semantic_fidelity' not in result.recursion_data:
                continue

            fidelity = result.recursion_data['semantic_fidelity']
            fidelity_scores.append({
                'task_id': result.task_id,
                'fidelity': fidelity,
                'depth': result.recursion_depth,
                'success': result.success
            })

        if not fidelity_scores:
            return {'error': 'No semantic fidelity data available'}

        scores = [f['fidelity'] for f in fidelity_scores]
        success_fidelity = [f['fidelity'] for f in fidelity_scores if f['success']]
        failure_fidelity = [f['fidelity'] for f in fidelity_scores if not f['success']]

        return {
            'mean_fidelity': np.mean(scores),
            'median_fidelity': np.median(scores),
            'fidelity_success_correlation': {
                'successful_tasks': np.mean(success_fidelity) if success_fidelity else 0,
                'failed_tasks': np.mean(failure_fidelity) if failure_fidelity else 0
            }
        }


class HallucinationDetector:
    """Detects hallucination patterns in recursive problem solving.

    Identifies when agents introduce claims, constraints, or reasoning
    patterns that aren't grounded in the original problem statement.
    """

    def __init__(self, results: List[EvaluationResult]):
        """Initialize with evaluation results containing recursion data."""
        self.results = [r for r in results if r.recursion_data is not None]

    def detect_ungrounded_claims(self) -> Dict[str, Any]:
        """Detect claims that aren't in the original problem statement.

        Returns:
            Dict containing hallucination detection metrics
        """
        hallucination_counts = []

        for result in self.results:
            if not result.recursion_data or 'hallucinations' not in result.recursion_data:
                continue

            hallucinations = result.recursion_data['hallucinations']
            ungrounded = hallucinations.get('ungrounded_claims', [])

            hallucination_counts.append({
                'task_id': result.task_id,
                'count': len(ungrounded),
                'depth': result.recursion_depth,
                'examples': ungrounded[:3] if ungrounded else []
            })

        if not hallucination_counts:
            return {'error': 'No hallucination data available'}

        counts = [h['count'] for h in hallucination_counts]
        tasks_with_hallucinations = sum(1 for c in counts if c > 0)

        return {
            'hallucination_rate': tasks_with_hallucinations / len(hallucination_counts) * 100,
            'mean_hallucinations_per_task': np.mean(counts),
            'max_hallucinations': np.max(counts),
            'total_hallucinations': sum(counts),
            'depth_correlation': self._correlate_with_depth(hallucination_counts)
        }

    def detect_invented_constraints(self) -> Dict[str, Any]:
        """Detect constraints that aren't in the original problem.

        Returns:
            Dict containing invented constraint metrics
        """
        constraint_counts = []

        for result in self.results:
            if not result.recursion_data or 'hallucinations' not in result.recursion_data:
                continue

            hallucinations = result.recursion_data['hallucinations']
            invented = hallucinations.get('invented_constraints', [])

            constraint_counts.append({
                'task_id': result.task_id,
                'count': len(invented),
                'depth': result.recursion_depth,
                'examples': invented[:3] if invented else []
            })

        if not constraint_counts:
            return {'error': 'No constraint invention data available'}

        counts = [c['count'] for c in constraint_counts]
        tasks_with_invented = sum(1 for c in counts if c > 0)

        return {
            'invention_rate': tasks_with_invented / len(constraint_counts) * 100,
            'mean_invented_per_task': np.mean(counts),
            'total_invented': sum(counts)
        }

    def detect_circular_reasoning(self) -> Dict[str, Any]:
        """Detect circular reasoning loops in recursive decomposition.

        Returns:
            Dict containing circular reasoning metrics
        """
        circular_patterns = []

        for result in self.results:
            if not result.recursion_data or 'circular_reasoning' not in result.recursion_data:
                continue

            circular = result.recursion_data['circular_reasoning']

            circular_patterns.append({
                'task_id': result.task_id,
                'has_circular': circular.get('detected', False),
                'loop_length': circular.get('loop_length', 0),
                'depth': result.recursion_depth
            })

        if not circular_patterns:
            return {'error': 'No circular reasoning data available'}

        has_circular = [p['has_circular'] for p in circular_patterns]
        loop_lengths = [p['loop_length'] for p in circular_patterns if p['loop_length'] > 0]

        return {
            'circular_reasoning_rate': sum(has_circular) / len(has_circular) * 100,
            'tasks_affected': sum(has_circular),
            'mean_loop_length': np.mean(loop_lengths) if loop_lengths else 0,
            'max_loop_length': np.max(loop_lengths) if loop_lengths else 0
        }

    def _correlate_with_depth(self, data: List[Dict]) -> Dict[str, Any]:
        """Correlate hallucination frequency with recursion depth."""
        if not data:
            return {}

        depths = [d['depth'] for d in data if d['depth'] is not None]
        counts = [d['count'] for d in data if d['depth'] is not None]

        if len(depths) < 2:
            return {'correlation': 0.0}

        correlation = np.corrcoef(depths, counts)[0, 1] if len(depths) > 1 else 0.0

        return {
            'correlation_coefficient': correlation,
            'interpretation': 'positive' if correlation > 0.3 else 'negative' if correlation < -0.3 else 'weak'
        }

    def generate_hallucination_summary(self) -> Dict[str, Any]:
        """Generate comprehensive hallucination summary across all detection types.

        Returns:
            Dict containing unified hallucination metrics
        """
        ungrounded = self.detect_ungrounded_claims()
        invented = self.detect_invented_constraints()
        circular = self.detect_circular_reasoning()

        return {
            'ungrounded_claims': ungrounded,
            'invented_constraints': invented,
            'circular_reasoning': circular,
            'overall_hallucination_score': self._calculate_overall_score(
                ungrounded, invented, circular
            )
        }

    def _calculate_overall_score(self, ungrounded: Dict, invented: Dict, circular: Dict) -> float:
        """Calculate an overall hallucination severity score (0-100)."""
        scores = []

        if 'hallucination_rate' in ungrounded and not isinstance(ungrounded.get('error'), str):
            scores.append(ungrounded['hallucination_rate'])
        if 'invention_rate' in invented and not isinstance(invented.get('error'), str):
            scores.append(invented['invention_rate'])
        if 'circular_reasoning_rate' in circular and not isinstance(circular.get('error'), str):
            scores.append(circular['circular_reasoning_rate'])

        return np.mean(scores) if scores else 0.0


class TerminalBenchStatisticalAnalyzer:
    """Complete statistical analysis for Terminal-Bench evaluation."""

    def __init__(self, results_dir: Path):
        """Initialize analyzer with results directory."""
        self.results_dir = Path(results_dir)
        self.amplifier_results: List[EvaluationResult] = []
        self.baseline_results: List[EvaluationResult] = []
        self.task_categories = self._load_task_categories()

    def _load_task_categories(self) -> Dict[str, str]:
        """Load task categorization from split.json."""
        split_file = self.results_dir / "split.json"
        if split_file.exists():
            with open(split_file) as f:
                data = json.load(f)
                # Create category mapping
                categories = {}
                for task in data.get("train", []):
                    # Infer category from task name
                    if "csv" in task or "data" in task:
                        categories[task] = "data_processing"
                    elif "pytorch" in task or "model" in task:
                        categories[task] = "machine_learning"
                    elif "git" in task or "docker" in task:
                        categories[task] = "devops"
                    elif "crack" in task or "security" in task:
                        categories[task] = "security"
                    else:
                        categories[task] = "general"
                return categories
        return {}

    def load_results(self, amplifier_dir: str, baseline_dir: str) -> None:
        """Load results from evaluation runs."""
        self.amplifier_results = self._load_agent_results(amplifier_dir)
        self.baseline_results = self._load_agent_results(baseline_dir)

        print(f"Loaded {len(self.amplifier_results)} Amplifier results")
        print(f"Loaded {len(self.baseline_results)} Baseline results")

    def _load_agent_results(self, agent_dir: str) -> List[EvaluationResult]:
        """Load results for a specific agent."""
        results = []
        results_file = Path(agent_dir) / "results.json"

        if results_file.exists():
            with open(results_file) as f:
                data = json.load(f)

            for result in data.get("results", []):
                # Extract metrics from result
                eval_result = EvaluationResult(
                    task_id=result.get("task_id"),
                    agent=agent_dir.split("/")[-1].split("_")[0],
                    success=result.get("success", False),
                    time_taken=result.get("time_taken", 0),
                    tokens_used=result.get("tokens_used", 0),
                    tool_calls=result.get("tool_calls", 0),
                    errors=result.get("errors", 0),
                    backtracks=result.get("backtracks", 0)
                )
                results.append(eval_result)

        return results

    def perform_primary_analysis(self) -> Dict[str, Any]:
        """Conduct primary statistical analysis."""
        if not stats:
            return {"error": "scipy not installed"}

        # Convert to success rates
        amp_successes = [r.success for r in self.amplifier_results]
        base_successes = [r.success for r in self.baseline_results]

        # Calculate success rates
        amp_rate = np.mean(amp_successes) * 100
        base_rate = np.mean(base_successes) * 100

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(
            amp_successes,
            base_successes,
            equal_var=False  # Welch's t-test
        )

        # Calculate effect size
        effect_size = self.calculate_cohens_d(amp_successes, base_successes)

        # Calculate confidence intervals
        ci_amp = self.calculate_confidence_interval(amp_successes)
        ci_base = self.calculate_confidence_interval(base_successes)

        # Determine statistical significance
        significant = p_value < 0.05

        return {
            'amplifier_success_rate': amp_rate,
            'baseline_success_rate': base_rate,
            'improvement': amp_rate - base_rate,
            't_statistic': t_stat,
            'p_value': p_value,
            'effect_size': effect_size,
            'effect_interpretation': self._interpret_effect_size(effect_size),
            'amplifier_ci': ci_amp,
            'baseline_ci': ci_base,
            'statistically_significant': significant,
            'reject_null_hypothesis': significant
        }

    def calculate_cohens_d(self, group1: List, group2: List) -> float:
        """Calculate Cohen's d effect size."""
        n1 = len(group1)
        n2 = len(group2)
        var1 = np.var(group1, ddof=1)
        var2 = np.var(group2, ddof=1)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))

        if pooled_std == 0:
            return 0

        return (np.mean(group1) - np.mean(group2)) / pooled_std

    def calculate_confidence_interval(self, data: List,
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for mean."""
        if not stats:
            return (0, 0)

        mean = np.mean(data)
        sem = stats.sem(data)
        margin = sem * stats.t.ppf((1 + confidence) / 2, len(data) - 1)

        return (mean - margin, mean + margin)

    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def perform_mann_whitney(self) -> Dict[str, Any]:
        """Non-parametric Mann-Whitney U test."""
        if not stats:
            return {"error": "scipy not installed"}

        amp_successes = [r.success for r in self.amplifier_results]
        base_successes = [r.success for r in self.baseline_results]

        u_stat, p_value = stats.mannwhitneyu(
            amp_successes,
            base_successes,
            alternative='two-sided'
        )

        return {
            'u_statistic': u_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    def check_assumptions(self) -> Dict[str, Any]:
        """Check statistical test assumptions."""
        if not stats:
            return {"error": "scipy not installed"}

        amp_successes = [r.success for r in self.amplifier_results]
        base_successes = [r.success for r in self.baseline_results]

        # Normality tests
        amp_shapiro = stats.shapiro(amp_successes)
        base_shapiro = stats.shapiro(base_successes)

        # Levene's test for homogeneity of variance
        levene_stat, levene_p = stats.levene(amp_successes, base_successes)

        return {
            'normality': {
                'amplifier': {
                    'statistic': amp_shapiro.statistic,
                    'p_value': amp_shapiro.pvalue,
                    'is_normal': amp_shapiro.pvalue > 0.05
                },
                'baseline': {
                    'statistic': base_shapiro.statistic,
                    'p_value': base_shapiro.pvalue,
                    'is_normal': base_shapiro.pvalue > 0.05
                }
            },
            'variance_homogeneity': {
                'statistic': levene_stat,
                'p_value': levene_p,
                'equal_variance': levene_p > 0.05
            },
            'use_parametric': (
                amp_shapiro.pvalue > 0.05 and
                base_shapiro.pvalue > 0.05
            ),
            'recommendation': 'Use t-test' if (amp_shapiro.pvalue > 0.05 and
                                              base_shapiro.pvalue > 0.05)
                            else 'Use Mann-Whitney U test'
        }

    def perform_category_analysis(self) -> Dict[str, Dict]:
        """Analyze performance by task category."""
        category_results = {}

        for category in set(self.task_categories.values()):
            # Filter results by category
            amp_cat = [r for r in self.amplifier_results
                      if self.task_categories.get(r.task_id) == category]
            base_cat = [r for r in self.baseline_results
                       if self.task_categories.get(r.task_id) == category]

            if amp_cat and base_cat:
                amp_rate = np.mean([r.success for r in amp_cat]) * 100
                base_rate = np.mean([r.success for r in base_cat]) * 100

                category_results[category] = {
                    'amplifier_success_rate': amp_rate,
                    'baseline_success_rate': base_rate,
                    'improvement': amp_rate - base_rate,
                    'n_tasks': len(amp_cat)
                }

        return category_results

    def calculate_power_analysis(self) -> Dict[str, Any]:
        """Calculate statistical power with actual sample size."""
        try:
            from statsmodels.stats.power import TTestPower
            power_analyzer = TTestPower()

            n = min(len(self.amplifier_results), len(self.baseline_results))

            # Calculate power for different effect sizes
            small_power = power_analyzer.solve_power(
                effect_size=0.2, nobs=n, alpha=0.05
            )
            medium_power = power_analyzer.solve_power(
                effect_size=0.5, nobs=n, alpha=0.05
            )
            large_power = power_analyzer.solve_power(
                effect_size=0.8, nobs=n, alpha=0.05
            )

            # Calculate minimum sample size for 0.80 power
            min_n_medium = power_analyzer.solve_power(
                effect_size=0.5, power=0.80, alpha=0.05
            )

            return {
                'current_sample_size': n,
                'power_small_effect': small_power,
                'power_medium_effect': medium_power,
                'power_large_effect': large_power,
                'min_n_for_medium_effect': int(min_n_medium),
                'adequate_power': medium_power >= 0.80
            }
        except ImportError:
            return {
                'error': 'statsmodels not installed',
                'current_sample_size': min(
                    len(self.amplifier_results),
                    len(self.baseline_results)
                )
            }

    def bootstrap_analysis(self, n_bootstrap: int = 10000) -> Dict[str, Any]:
        """Perform bootstrap analysis for robust confidence intervals."""
        amp_successes = [r.success for r in self.amplifier_results]
        base_successes = [r.success for r in self.baseline_results]

        differences = []
        for _ in range(n_bootstrap):
            # Resample with replacement
            amp_sample = np.random.choice(amp_successes, size=len(amp_successes), replace=True)
            base_sample = np.random.choice(base_successes, size=len(base_successes), replace=True)

            # Calculate difference in means
            diff = np.mean(amp_sample) - np.mean(base_sample)
            differences.append(diff)

        # Calculate bootstrap confidence interval
        ci_lower = np.percentile(differences, 2.5) * 100
        ci_upper = np.percentile(differences, 97.5) * 100
        mean_diff = np.mean(differences) * 100

        return {
            'bootstrap_mean_difference': mean_diff,
            'bootstrap_ci_lower': ci_lower,
            'bootstrap_ci_upper': ci_upper,
            'significant': ci_lower > 0  # Significant if CI doesn't include 0
        }

    def analyze_recursion_metrics(self) -> Dict[str, Any]:
        """Analyze recursion-specific metrics using specialized analyzers.

        Integrates RecursionMetricsAnalyzer, SemanticDriftAnalyzer, and
        HallucinationDetector to provide comprehensive recursion analysis.

        Returns:
            Dict containing all recursion-specific analyses
        """
        # Check if we have recursion data
        amp_with_recursion = [r for r in self.amplifier_results if r.recursion_data is not None]
        base_with_recursion = [r for r in self.baseline_results if r.recursion_data is not None]

        if not amp_with_recursion and not base_with_recursion:
            return {'error': 'No recursion data available in results'}

        results = {
            'amplifier': {},
            'baseline': {},
            'comparison': {}
        }

        # Analyze Amplifier
        if amp_with_recursion:
            recursion_analyzer = RecursionMetricsAnalyzer(amp_with_recursion)
            semantic_analyzer = SemanticDriftAnalyzer(amp_with_recursion)
            hallucination_detector = HallucinationDetector(amp_with_recursion)

            results['amplifier'] = {
                'recursion_metrics': {
                    'depth_achieved': recursion_analyzer.analyze_max_depth_achieved(),
                    'degradation_curves': recursion_analyzer.analyze_depth_degradation_curves(),
                    'stack_efficiency': recursion_analyzer.analyze_stack_efficiency(),
                    'branching_consistency': recursion_analyzer.analyze_branching_consistency()
                },
                'semantic_drift': {
                    'fact_retention': semantic_analyzer.calculate_fact_retention_score(),
                    'information_loss': semantic_analyzer.track_information_loss_per_depth(),
                    'semantic_fidelity': semantic_analyzer.calculate_semantic_fidelity_metrics()
                },
                'hallucinations': hallucination_detector.generate_hallucination_summary()
            }

        # Analyze Baseline
        if base_with_recursion:
            recursion_analyzer = RecursionMetricsAnalyzer(base_with_recursion)
            semantic_analyzer = SemanticDriftAnalyzer(base_with_recursion)
            hallucination_detector = HallucinationDetector(base_with_recursion)

            results['baseline'] = {
                'recursion_metrics': {
                    'depth_achieved': recursion_analyzer.analyze_max_depth_achieved(),
                    'degradation_curves': recursion_analyzer.analyze_depth_degradation_curves(),
                    'stack_efficiency': recursion_analyzer.analyze_stack_efficiency(),
                    'branching_consistency': recursion_analyzer.analyze_branching_consistency()
                },
                'semantic_drift': {
                    'fact_retention': semantic_analyzer.calculate_fact_retention_score(),
                    'information_loss': semantic_analyzer.track_information_loss_per_depth(),
                    'semantic_fidelity': semantic_analyzer.calculate_semantic_fidelity_metrics()
                },
                'hallucinations': hallucination_detector.generate_hallucination_summary()
            }

        # Comparative analysis
        if amp_with_recursion and base_with_recursion:
            results['comparison'] = self._compare_recursion_metrics(
                results['amplifier'],
                results['baseline']
            )

        return results

    def _compare_recursion_metrics(self, amp_metrics: Dict, base_metrics: Dict) -> Dict[str, Any]:
        """Compare recursion metrics between Amplifier and Baseline.

        Args:
            amp_metrics: Amplifier recursion metrics
            base_metrics: Baseline recursion metrics

        Returns:
            Dict containing comparative analysis
        """
        comparison = {}

        # Compare depth achieved
        amp_depth = amp_metrics.get('recursion_metrics', {}).get('depth_achieved', {})
        base_depth = base_metrics.get('recursion_metrics', {}).get('depth_achieved', {})

        if 'error' not in amp_depth and 'error' not in base_depth:
            comparison['depth_comparison'] = {
                'amplifier_mean': amp_depth.get('mean_depth', 0),
                'baseline_mean': base_depth.get('mean_depth', 0),
                'difference': amp_depth.get('mean_depth', 0) - base_depth.get('mean_depth', 0),
                'amplifier_max': amp_depth.get('max_depth', 0),
                'baseline_max': base_depth.get('max_depth', 0)
            }

        # Compare semantic fidelity
        amp_fidelity = amp_metrics.get('semantic_drift', {}).get('semantic_fidelity', {})
        base_fidelity = base_metrics.get('semantic_drift', {}).get('semantic_fidelity', {})

        if 'error' not in amp_fidelity and 'error' not in base_fidelity:
            comparison['fidelity_comparison'] = {
                'amplifier_mean': amp_fidelity.get('mean_fidelity', 0),
                'baseline_mean': base_fidelity.get('mean_fidelity', 0),
                'difference': amp_fidelity.get('mean_fidelity', 0) - base_fidelity.get('mean_fidelity', 0)
            }

        # Compare hallucination rates
        amp_hall = amp_metrics.get('hallucinations', {})
        base_hall = base_metrics.get('hallucinations', {})

        amp_score = amp_hall.get('overall_hallucination_score', 0)
        base_score = base_hall.get('overall_hallucination_score', 0)

        comparison['hallucination_comparison'] = {
            'amplifier_score': amp_score,
            'baseline_score': base_score,
            'difference': amp_score - base_score,
            'interpretation': 'Amplifier lower' if amp_score < base_score else 'Baseline lower'
        }

        return comparison

    def generate_report(self) -> str:
        """Generate comprehensive statistical report in Markdown."""
        report = []
        report.append("# Terminal-Bench Statistical Analysis Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Primary Analysis
        report.append("\n## 1. Primary Analysis Results")
        primary = self.perform_primary_analysis()

        if "error" not in primary:
            report.append("\n### Success Rates")
            report.append(f"- **Amplifier**: {primary['amplifier_success_rate']:.1f}% "
                        f"(95% CI: {primary['amplifier_ci'][0]:.1f}-{primary['amplifier_ci'][1]:.1f})")
            report.append(f"- **Baseline**: {primary['baseline_success_rate']:.1f}% "
                        f"(95% CI: {primary['baseline_ci'][0]:.1f}-{primary['baseline_ci'][1]:.1f})")
            report.append(f"- **Improvement**: {primary['improvement']:.1f}%")

            report.append("\n### Statistical Significance")
            report.append(f"- **t-statistic**: {primary['t_statistic']:.4f}")
            report.append(f"- **p-value**: {primary['p_value']:.4f}")
            report.append(f"- **Effect Size (Cohen's d)**: {primary['effect_size']:.3f} ({primary['effect_interpretation']})")
            report.append(f"- **Statistically Significant**: {'✅ Yes' if primary['statistically_significant'] else '❌ No'}")

        # Assumptions Check
        report.append("\n## 2. Statistical Assumptions")
        assumptions = self.check_assumptions()

        if "error" not in assumptions:
            report.append("\n### Normality Tests")
            for agent in ['amplifier', 'baseline']:
                norm = assumptions['normality'][agent]
                report.append(f"- **{agent.capitalize()}**: "
                            f"Shapiro-Wilk p={norm['p_value']:.4f} "
                            f"({'✅ Normal' if norm['is_normal'] else '⚠️ Non-normal'})")

            report.append("\n### Variance Homogeneity")
            var = assumptions['variance_homogeneity']
            report.append(f"- **Levene's Test**: p={var['p_value']:.4f} "
                        f"({'✅ Equal variance' if var['equal_variance'] else '⚠️ Unequal variance'})")

            report.append(f"\n**Recommendation**: {assumptions['recommendation']}")

        # Non-parametric Analysis
        report.append("\n## 3. Non-Parametric Analysis")
        mann_whitney = self.perform_mann_whitney()

        if "error" not in mann_whitney:
            report.append(f"- **Mann-Whitney U statistic**: {mann_whitney['u_statistic']:.1f}")
            report.append(f"- **p-value**: {mann_whitney['p_value']:.4f}")
            report.append(f"- **Significant**: {'✅ Yes' if mann_whitney['significant'] else '❌ No'}")

        # Power Analysis
        report.append("\n## 4. Statistical Power")
        power = self.calculate_power_analysis()

        if "error" not in power:
            report.append(f"- **Sample Size**: {power['current_sample_size']} per group")
            report.append(f"- **Power (small effect)**: {power['power_small_effect']:.2f}")
            report.append(f"- **Power (medium effect)**: {power['power_medium_effect']:.2f}")
            report.append(f"- **Power (large effect)**: {power['power_large_effect']:.2f}")
            report.append(f"- **Adequate Power**: {'✅ Yes' if power['adequate_power'] else '⚠️ No (need n≥' + str(power['min_n_for_medium_effect']) + ')'}")

        # Bootstrap Analysis
        report.append("\n## 5. Bootstrap Analysis")
        bootstrap_results = self.bootstrap_analysis()

        report.append(f"- **Mean Difference**: {bootstrap_results['bootstrap_mean_difference']:.1f}%")
        report.append(f"- **95% Bootstrap CI**: [{bootstrap_results['bootstrap_ci_lower']:.1f}, "
                     f"{bootstrap_results['bootstrap_ci_upper']:.1f}]")
        report.append(f"- **Significant**: {'✅ Yes (CI excludes 0)' if bootstrap_results['significant'] else '❌ No (CI includes 0)'}")

        # Category Analysis
        report.append("\n## 6. Performance by Category")
        categories = self.perform_category_analysis()

        if categories:
            report.append("\n| Category | Amplifier | Baseline | Improvement | N |")
            report.append("|----------|-----------|----------|-------------|---|")
            for cat, metrics in categories.items():
                report.append(f"| {cat} | {metrics['amplifier_success_rate']:.1f}% | "
                            f"{metrics['baseline_success_rate']:.1f}% | "
                            f"{metrics['improvement']:+.1f}% | "
                            f"{metrics['n_tasks']} |")

        # Recursion Metrics Analysis
        recursion_metrics = self.analyze_recursion_metrics()

        if 'error' not in recursion_metrics:
            report.append("\n## 7. Recursion-Specific Analysis")

            # Amplifier recursion metrics
            if 'amplifier' in recursion_metrics and recursion_metrics['amplifier']:
                report.append("\n### 7.1 Amplifier Recursion Metrics")

                amp_metrics = recursion_metrics['amplifier']

                # Depth analysis
                depth_data = amp_metrics.get('recursion_metrics', {}).get('depth_achieved', {})
                if 'error' not in depth_data:
                    report.append("\n#### Recursion Depth")
                    report.append(f"- **Mean Depth**: {depth_data.get('mean_depth', 0):.2f}")
                    report.append(f"- **Max Depth**: {depth_data.get('max_depth', 0)}")
                    report.append(f"- **Median Depth**: {depth_data.get('median_depth', 0):.2f}")

                    dist = depth_data.get('depth_distribution', {})
                    report.append(f"- **Depth Distribution**: Shallow: {dist.get('shallow (1-2)', 0)}, "
                                f"Medium: {dist.get('medium (3-5)', 0)}, Deep: {dist.get('deep (6+)', 0)}")

                # Degradation curves
                degradation = amp_metrics.get('recursion_metrics', {}).get('degradation_curves', {})
                if 'error' not in degradation:
                    report.append("\n#### Performance Degradation")
                    report.append(f"- **Degradation Detected**: "
                                f"{'Yes' if degradation.get('degradation_detected') else 'No'}")

                    curve = degradation.get('curve', {})
                    if curve:
                        report.append("- **Success Rate by Depth**:")
                        for depth_key, metrics in sorted(curve.items()):
                            report.append(f"  - {depth_key}: {metrics['success_rate']:.1f}% "
                                        f"(n={metrics['n_tasks']})")

                # Semantic drift
                semantic = amp_metrics.get('semantic_drift', {})
                fidelity = semantic.get('semantic_fidelity', {})
                if 'error' not in fidelity:
                    report.append("\n#### Semantic Fidelity")
                    report.append(f"- **Mean Fidelity**: {fidelity.get('mean_fidelity', 0):.3f}")
                    report.append(f"- **Successful Tasks**: "
                                f"{fidelity.get('fidelity_success_correlation', {}).get('successful_tasks', 0):.3f}")

                # Hallucinations
                hallucinations = amp_metrics.get('hallucinations', {})
                if hallucinations:
                    report.append("\n#### Hallucination Detection")
                    ungrounded = hallucinations.get('ungrounded_claims', {})
                    if 'error' not in ungrounded:
                        report.append(f"- **Hallucination Rate**: {ungrounded.get('hallucination_rate', 0):.1f}%")

                    circular = hallucinations.get('circular_reasoning', {})
                    if 'error' not in circular:
                        report.append(f"- **Circular Reasoning Rate**: "
                                    f"{circular.get('circular_reasoning_rate', 0):.1f}%")

                    overall_score = hallucinations.get('overall_hallucination_score', 0)
                    report.append(f"- **Overall Hallucination Score**: {overall_score:.1f}/100")

            # Baseline recursion metrics
            if 'baseline' in recursion_metrics and recursion_metrics['baseline']:
                report.append("\n### 7.2 Baseline Recursion Metrics")

                base_metrics = recursion_metrics['baseline']

                # Depth analysis
                depth_data = base_metrics.get('recursion_metrics', {}).get('depth_achieved', {})
                if 'error' not in depth_data:
                    report.append("\n#### Recursion Depth")
                    report.append(f"- **Mean Depth**: {depth_data.get('mean_depth', 0):.2f}")
                    report.append(f"- **Max Depth**: {depth_data.get('max_depth', 0)}")

                # Hallucinations
                hallucinations = base_metrics.get('hallucinations', {})
                if hallucinations:
                    overall_score = hallucinations.get('overall_hallucination_score', 0)
                    report.append(f"- **Overall Hallucination Score**: {overall_score:.1f}/100")

            # Comparison
            if 'comparison' in recursion_metrics and recursion_metrics['comparison']:
                report.append("\n### 7.3 Recursion Comparison")

                comparison = recursion_metrics['comparison']

                depth_comp = comparison.get('depth_comparison', {})
                if depth_comp:
                    report.append("\n#### Depth Comparison")
                    report.append(f"- **Amplifier Mean**: {depth_comp.get('amplifier_mean', 0):.2f}")
                    report.append(f"- **Baseline Mean**: {depth_comp.get('baseline_mean', 0):.2f}")
                    report.append(f"- **Difference**: {depth_comp.get('difference', 0):+.2f}")

                hall_comp = comparison.get('hallucination_comparison', {})
                if hall_comp:
                    report.append("\n#### Hallucination Comparison")
                    report.append(f"- **Amplifier Score**: {hall_comp.get('amplifier_score', 0):.1f}")
                    report.append(f"- **Baseline Score**: {hall_comp.get('baseline_score', 0):.1f}")
                    report.append(f"- **Interpretation**: {hall_comp.get('interpretation', 'N/A')}")

        # Conclusions
        report.append("\n## 8. Conclusions")

        if "error" not in primary:
            if primary['statistically_significant']:
                report.append(f"\n✅ **Result**: The null hypothesis is REJECTED. "
                            f"Amplifier shows statistically significant improvement "
                            f"({primary['improvement']:.1f}%, p={primary['p_value']:.4f}) "
                            f"with a {primary['effect_interpretation']} effect size.")
            else:
                report.append(f"\n❌ **Result**: The null hypothesis is NOT rejected. "
                            f"No statistically significant difference found "
                            f"(p={primary['p_value']:.4f}).")

        return "\n".join(report)


def main():
    """Example usage of the statistical analyzer."""
    # Example usage
    analyzer = TerminalBenchStatisticalAnalyzer(Path("recursioneval"))

    # This would load actual results
    # analyzer.load_results(
    #     "ai_working/tmp/amplifier_train_2025-10-30",
    #     "ai_working/tmp/baseline_train_2025-10-30"
    # )

    # Generate and save report
    # report = analyzer.generate_report()
    # with open("statistical_report.md", "w") as f:
    #     f.write(report)

    print("Statistical Analysis Module Ready")
    print("Use: analyzer.load_results(amplifier_dir, baseline_dir)")
    print("Then: report = analyzer.generate_report()")


if __name__ == "__main__":
    main()