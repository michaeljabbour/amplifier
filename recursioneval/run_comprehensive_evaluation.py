#!/usr/bin/env python3
"""
Comprehensive Terminal-Bench Evaluation Runner with Full Analysis

This script orchestrates the complete evaluation pipeline including:
1. Running evaluations for both agents
2. Performing statistical analysis
3. Analyzing reasoning traces
4. Generating comprehensive reports
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import our analysis modules
from statistical_analysis import TerminalBenchStatisticalAnalyzer
from reasoning_trace_analyzer import ReasoningTraceAnalyzer


class ComprehensiveEvaluator:
    """Orchestrates the complete evaluation pipeline."""

    def __init__(self, base_dir: Path = None):
        """Initialize the evaluator."""
        self.base_dir = base_dir or Path.cwd()
        self.results_dir = self.base_dir / "ai_working" / "tmp"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.statistical_analyzer = TerminalBenchStatisticalAnalyzer(self.base_dir)
        self.reasoning_analyzer = ReasoningTraceAnalyzer()

        self.amplifier_run_dir = None
        self.baseline_run_dir = None

    def run_evaluation(self, agent: str, split: str = "small",
                      concurrent: int = 3, model: str = None) -> Path:
        """Run terminal-bench evaluation for specified agent."""
        timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
        run_id = f"{agent}_{split}_{timestamp}"

        print(f"\n{'='*60}")
        print(f"🚀 Starting {agent.upper()} evaluation")
        print(f"   Split: {split}")
        print(f"   Run ID: {run_id}")
        print(f"{'='*60}\n")

        # Build command
        cmd = [
            "uv", "run", str(self.base_dir / "run_full_evaluation.py"),
            "--agent", agent,
            "--split", split,
            "--concurrent", str(concurrent)
        ]

        if model:
            cmd.extend(["--model", model])

        # Run evaluation
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)

            run_dir = self.results_dir / run_id
            if run_dir.exists():
                print(f"✅ {agent} evaluation complete: {run_dir}")
                return run_dir
            else:
                print(f"⚠️ Run directory not found: {run_dir}")
                return None

        except subprocess.CalledProcessError as e:
            print(f"❌ Evaluation failed: {e}")
            print(f"Error output: {e.stderr}")
            return None

    def analyze_reasoning_traces(self, run_dir: Path, agent: str) -> Dict[str, Any]:
        """Analyze reasoning traces for all tasks in a run."""
        print(f"\n📊 Analyzing reasoning traces for {agent}...")

        all_analyses = []
        task_dirs = [d for d in run_dir.iterdir() if d.is_dir()]

        for task_dir in task_dirs:
            # Find agent log
            agent_logs = list(task_dir.glob("*/sessions/agent.log"))
            if agent_logs:
                log_path = agent_logs[0]
                task_id = task_dir.name

                try:
                    analysis = self.reasoning_analyzer.analyze_log(log_path, task_id)
                    all_analyses.append(analysis)
                except Exception as e:
                    print(f"  ⚠️ Failed to analyze {task_id}: {e}")

        # Aggregate metrics
        if all_analyses:
            aggregated = {
                'agent': agent,
                'total_tasks_analyzed': len(all_analyses),
                'avg_planning_depth': sum(a['patterns']['planning_depth']
                                         for a in all_analyses) / len(all_analyses),
                'avg_backtrack_count': sum(a['patterns']['backtrack_count']
                                          for a in all_analyses) / len(all_analyses),
                'avg_error_recovery': sum(a['patterns']['error_recovery_rate']
                                         for a in all_analyses) / len(all_analyses),
                'avg_reasoning_efficiency': sum(a['reasoning_efficiency']
                                               for a in all_analyses) / len(all_analyses),
                'individual_analyses': all_analyses
            }

            print(f"  ✅ Analyzed {len(all_analyses)} tasks")
            print(f"  📈 Avg Planning Depth: {aggregated['avg_planning_depth']:.2f}")
            print(f"  🔄 Avg Backtracks: {aggregated['avg_backtrack_count']:.2f}")
            print(f"  💪 Avg Error Recovery: {aggregated['avg_error_recovery']:.2%}")
            print(f"  ⚡ Avg Efficiency: {aggregated['avg_reasoning_efficiency']:.2f}")

            return aggregated

        return {}

    def perform_statistical_analysis(self, amplifier_dir: Path,
                                    baseline_dir: Path) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis."""
        print("\n📊 Performing statistical analysis...")

        # Load results
        self.statistical_analyzer.load_results(str(amplifier_dir), str(baseline_dir))

        # Run all analyses
        results = {
            'primary': self.statistical_analyzer.perform_primary_analysis(),
            'assumptions': self.statistical_analyzer.check_assumptions(),
            'mann_whitney': self.statistical_analyzer.perform_mann_whitney(),
            'power': self.statistical_analyzer.calculate_power_analysis(),
            'bootstrap': self.statistical_analyzer.bootstrap_analysis(),
            'categories': self.statistical_analyzer.perform_category_analysis()
        }

        # Print summary
        primary = results['primary']
        if 'error' not in primary:
            print(f"\n  📈 Amplifier Success Rate: {primary['amplifier_success_rate']:.1f}%")
            print(f"  📉 Baseline Success Rate: {primary['baseline_success_rate']:.1f}%")
            print(f"  🎯 Improvement: {primary['improvement']:.1f}%")
            print(f"  📊 p-value: {primary['p_value']:.4f}")
            print(f"  🎲 Effect Size: {primary['effect_size']:.3f} ({primary['effect_interpretation']})")
            print(f"  ✨ Statistically Significant: {'✅ Yes' if primary['statistically_significant'] else '❌ No'}")

        return results

    def generate_comprehensive_report(self, amplifier_dir: Path,
                                     baseline_dir: Path,
                                     output_path: Path = None) -> None:
        """Generate comprehensive evaluation report."""
        print("\n📝 Generating comprehensive report...")

        if not output_path:
            output_path = self.results_dir / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        report = []
        report.append("# Comprehensive Terminal-Bench Evaluation Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nAmplifier Run: {amplifier_dir.name}")
        report.append(f"Baseline Run: {baseline_dir.name}")

        # 1. Statistical Analysis Section
        report.append("\n## 1. Statistical Analysis")
        stat_report = self.statistical_analyzer.generate_report()
        report.append(stat_report)

        # 2. Reasoning Trace Analysis Section
        report.append("\n## 2. Reasoning Pattern Analysis")

        # Analyze both agents
        amp_reasoning = self.analyze_reasoning_traces(amplifier_dir, "amplifier")
        base_reasoning = self.analyze_reasoning_traces(baseline_dir, "baseline")

        report.append("\n### Amplifier Reasoning Patterns")
        if amp_reasoning:
            report.append(f"- Average Planning Depth: {amp_reasoning['avg_planning_depth']:.2f}")
            report.append(f"- Average Backtracks: {amp_reasoning['avg_backtrack_count']:.2f}")
            report.append(f"- Error Recovery Rate: {amp_reasoning['avg_error_recovery']:.2%}")
            report.append(f"- Reasoning Efficiency: {amp_reasoning['avg_reasoning_efficiency']:.2f}")

        report.append("\n### Baseline Reasoning Patterns")
        if base_reasoning:
            report.append(f"- Average Planning Depth: {base_reasoning['avg_planning_depth']:.2f}")
            report.append(f"- Average Backtracks: {base_reasoning['avg_backtrack_count']:.2f}")
            report.append(f"- Error Recovery Rate: {base_reasoning['avg_error_recovery']:.2%}")
            report.append(f"- Reasoning Efficiency: {base_reasoning['avg_reasoning_efficiency']:.2f}")

        # 3. Comparative Analysis
        report.append("\n## 3. Comparative Analysis")
        if amp_reasoning and base_reasoning:
            report.append("\n### Reasoning Improvements")
            report.append(f"- Planning Depth: {amp_reasoning['avg_planning_depth'] - base_reasoning['avg_planning_depth']:+.2f}")
            report.append(f"- Backtrack Reduction: {base_reasoning['avg_backtrack_count'] - amp_reasoning['avg_backtrack_count']:+.2f}")
            report.append(f"- Error Recovery: {(amp_reasoning['avg_error_recovery'] - base_reasoning['avg_error_recovery'])*100:+.1f}%")
            report.append(f"- Efficiency Gain: {amp_reasoning['avg_reasoning_efficiency'] - base_reasoning['avg_reasoning_efficiency']:+.2f}")

        # 4. Key Findings
        report.append("\n## 4. Key Findings")
        report.append(self._generate_key_findings())

        # 5. Recommendations
        report.append("\n## 5. Recommendations")
        report.append(self._generate_recommendations())

        # Save report
        full_report = "\n".join(report)
        with open(output_path, 'w') as f:
            f.write(full_report)

        print(f"  ✅ Report saved to: {output_path}")

    def _generate_key_findings(self) -> str:
        """Generate key findings section."""
        findings = []
        findings.append("\n### Statistical Findings")
        findings.append("- Primary hypothesis testing results")
        findings.append("- Effect size interpretation")
        findings.append("- Power analysis results")

        findings.append("\n### Reasoning Pattern Findings")
        findings.append("- Differences in planning approaches")
        findings.append("- Error recovery strategies")
        findings.append("- Tool usage patterns")

        findings.append("\n### Performance Categories")
        findings.append("- Best performing task categories")
        findings.append("- Challenging task types")
        findings.append("- Unexpected results")

        return "\n".join(findings)

    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        recs = []
        recs.append("\n### For Amplifier Development")
        recs.append("- Focus on improving specific weak areas")
        recs.append("- Enhance error recovery mechanisms")
        recs.append("- Optimize reasoning efficiency")

        recs.append("\n### For Future Evaluation")
        recs.append("- Increase sample size for better power")
        recs.append("- Add more diverse task categories")
        recs.append("- Implement real-time monitoring")

        return "\n".join(recs)

    def run_complete_pipeline(self, split: str = "small",
                            concurrent: int = 3,
                            model: str = None) -> None:
        """Run the complete evaluation pipeline."""
        print("\n" + "="*70)
        print(" COMPREHENSIVE TERMINAL-BENCH EVALUATION PIPELINE")
        print("="*70)

        # Step 1: Run Amplifier Evaluation
        print("\n📌 STEP 1: Running Amplifier Evaluation")
        self.amplifier_run_dir = self.run_evaluation("amplifier", split, concurrent, model)

        if not self.amplifier_run_dir:
            print("❌ Amplifier evaluation failed. Aborting.")
            return

        # Step 2: Run Baseline Evaluation
        print("\n📌 STEP 2: Running Baseline Evaluation")
        self.baseline_run_dir = self.run_evaluation("baseline", split, concurrent, model)

        if not self.baseline_run_dir:
            print("❌ Baseline evaluation failed. Aborting.")
            return

        # Step 3: Statistical Analysis
        print("\n📌 STEP 3: Performing Statistical Analysis")
        stats_results = self.perform_statistical_analysis(
            self.amplifier_run_dir,
            self.baseline_run_dir
        )

        # Step 4: Generate Report
        print("\n📌 STEP 4: Generating Comprehensive Report")
        self.generate_comprehensive_report(
            self.amplifier_run_dir,
            self.baseline_run_dir
        )

        print("\n" + "="*70)
        print(" ✅ EVALUATION COMPLETE")
        print("="*70)

        # Print summary
        print("\nSUMMARY:")
        print(f"  Amplifier Results: {self.amplifier_run_dir}")
        print(f"  Baseline Results: {self.baseline_run_dir}")
        print(f"  Statistical Report: {self.results_dir}/comprehensive_report_*.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive Terminal-Bench evaluation with full analysis"
    )

    parser.add_argument(
        "--split",
        choices=["small", "train", "test", "both"],
        default="small",
        help="Task split to use (default: small for testing)"
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=3,
        help="Number of concurrent tasks (default: 3)"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Model to use (e.g., claude-3-5-sonnet-latest)"
    )

    parser.add_argument(
        "--amplifier-dir",
        type=Path,
        help="Existing Amplifier results directory (skip evaluation)"
    )

    parser.add_argument(
        "--baseline-dir",
        type=Path,
        help="Existing Baseline results directory (skip evaluation)"
    )

    parser.add_argument(
        "--analysis-only",
        action="store_true",
        help="Only run analysis on existing results"
    )

    args = parser.parse_args()

    evaluator = ComprehensiveEvaluator(Path.cwd())

    if args.analysis_only:
        # Only run analysis on existing results
        if not args.amplifier_dir or not args.baseline_dir:
            print("❌ --analysis-only requires --amplifier-dir and --baseline-dir")
            sys.exit(1)

        print("Running analysis only on existing results...")
        stats_results = evaluator.perform_statistical_analysis(
            args.amplifier_dir,
            args.baseline_dir
        )
        evaluator.generate_comprehensive_report(
            args.amplifier_dir,
            args.baseline_dir
        )
    else:
        # Run complete pipeline
        evaluator.run_complete_pipeline(
            split=args.split,
            concurrent=args.concurrent,
            model=args.model
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())