#!/usr/bin/env python3
"""
Full Terminal-Bench Evaluation Runner for Amplifier

This script runs the complete terminal-bench evaluation suite for Amplifier,
comparing it against a baseline Claude Code agent.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from custom_harness import create_harness


def load_task_split(split_file: Path) -> Dict[str, List[str]]:
    """Load the task split configuration."""
    with split_file.open() as f:
        return json.load(f)


def run_evaluation(
    agent: str,
    task_ids: List[str],
    output_dir: Path,
    run_id: str,
    n_concurrent_trials: int = 5,
    n_attempts: int = 1,
    timeout_multiplier: float = 2.0,
    model_name: str | None = None
) -> Dict[str, Any]:
    """Run the terminal-bench evaluation."""

    print(f"🚀 Starting Terminal-Bench Evaluation")
    print(f"📊 Agent: {agent}")
    print(f"📝 Tasks: {len(task_ids)} tasks")
    print(f"🔧 Concurrent trials: {n_concurrent_trials}")
    print(f"🔄 Attempts per task: {n_attempts}")
    print(f"⏱️  Timeout multiplier: {timeout_multiplier}")
    if model_name:
        print(f"🤖 Model: {model_name}")
    print(f"📁 Output: {output_dir / run_id}")
    print("-" * 50)

    # Use create_harness to get a CleanHarness instance
    harness = create_harness(
        agent=agent,
        task_ids=task_ids,
        output_dir=output_dir,
        run_id=run_id,
        n_concurrent_trials=n_concurrent_trials,
        n_attempts=n_attempts,
        timeout_multiplier=timeout_multiplier,
        model_name=model_name
    )

    # Run evaluation
    print("\n🏃 Running evaluation...")
    results = harness.run()

    # Custom harness should prevent nested structures, but call cleanup just in case
    print("\n📁 Ensuring clean directory structure...")
    try:
        # The CleanHarness already handles this, but we can double-check
        from utils.flatten_results import flatten_results_structure
        flatten_results_structure(output_dir, run_id)
    except Exception as e:
        print(f"ℹ️  Directory structure cleanup: {e}")

    return results


def analyze_results(results) -> Dict[str, Any]:
    """Analyze the evaluation results."""
    # Handle BenchmarkResults object from terminal-bench
    if hasattr(results, 'results'):
        results_list = results.results
    elif isinstance(results, list):
        results_list = results
    else:
        # Try to extract results from the object
        results_list = []
        if hasattr(results, '__dict__'):
            for key, value in results.__dict__.items():
                if 'results' in key.lower() and isinstance(value, list):
                    results_list = value
                    break

    total = len(results_list) if results_list else 0
    # Terminal-bench uses 'is_resolved' field, not 'success'
    successful = sum(1 for r in results_list if (
        r.get("is_resolved", False) if isinstance(r, dict)
        else getattr(r, 'is_resolved', getattr(r, 'success', False))
    ))
    failed = total - successful

    # Group failures by type
    failure_types = {}
    for result in results_list:
        if isinstance(result, dict):
            if not result.get("is_resolved", result.get("success", False)):
                task_id = result.get("task_id", "unknown")
                error = result.get("error", "unknown error")
                failure_types[task_id] = error[:200] if isinstance(error, str) else str(error)[:200]
        else:
            # Handle object-based results
            if not getattr(result, 'is_resolved', getattr(result, 'success', False)):
                task_id = getattr(result, 'task_id', 'unknown')
                error = getattr(result, 'error', 'unknown error')
                failure_types[task_id] = str(error)[:200]

    return {
        "total_tasks": total,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "failure_types": failure_types
    }


def save_results(
    results: Dict[str, Any],
    analysis: Dict[str, Any],
    output_file: Path
) -> None:
    """Save results and analysis to file."""
    # Convert BenchmarkResults to serializable format
    serializable_results = None
    if hasattr(results, 'results'):
        # Extract results list from BenchmarkResults object
        serializable_results = []
        for r in results.results:
            if hasattr(r, '__dict__'):
                # Convert each result object to dict
                result_dict = {}
                for key, value in r.__dict__.items():
                    try:
                        # Try to serialize to check if it's JSON-safe
                        json.dumps(value)
                        result_dict[key] = value
                    except (TypeError, ValueError):
                        # Skip non-serializable fields
                        result_dict[key] = str(value)
                serializable_results.append(result_dict)
            else:
                serializable_results.append(r)
    elif isinstance(results, list):
        serializable_results = results
    else:
        # Try to convert to dict if it has attributes
        if hasattr(results, '__dict__'):
            serializable_results = {k: v for k, v in results.__dict__.items()
                                   if not k.startswith('_')}
        else:
            serializable_results = results

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "raw_results": serializable_results
    }

    with output_file.open("w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n💾 Results saved to: {output_file}")


def print_summary(analysis: Dict[str, Any]) -> None:
    """Print evaluation summary."""
    print("\n" + "=" * 50)
    print("📊 EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total tasks:    {analysis['total_tasks']}")
    print(f"Successful:     {analysis['successful']}")
    print(f"Failed:         {analysis['failed']}")
    print(f"Success rate:   {analysis['success_rate']:.1f}%")

    if analysis['failed'] > 0:
        print("\n❌ Failed tasks:")
        for task_id, error in list(analysis['failure_types'].items())[:10]:
            print(f"  - {task_id}: {error}")

        if len(analysis['failure_types']) > 10:
            print(f"  ... and {len(analysis['failure_types']) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="Run full terminal-bench evaluation for Amplifier"
    )
    parser.add_argument(
        "--agent",
        choices=["amplifier", "baseline", "both"],
        default="amplifier",
        help="Agent type to evaluate (default: amplifier)"
    )
    parser.add_argument(
        "--split",
        choices=["train", "test", "both", "small"],
        default="train",
        help="Task split to use (default: train)"
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Number of concurrent trials (default: 10)"
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=1,
        help="Number of attempts per task (default: 1)"
    )
    parser.add_argument(
        "--timeout-multiplier",
        type=float,
        default=2.0,
        help="Timeout multiplier (default: 2.0)"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model name to use (e.g., claude-3-5-sonnet-latest)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: results/)"
    )

    args = parser.parse_args()

    # Setup paths
    split_file = Path(__file__).parent / "split.json"
    # Default to results/ directory in the project root
    output_dir = args.output_dir or Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load task split
    split_data = load_task_split(split_file)

    # Determine tasks to run
    if args.split == "train":
        task_ids = split_data["train"]
    elif args.split == "test":
        task_ids = split_data["test"]
    elif args.split == "both":
        task_ids = split_data["train"] + split_data["test"]
    elif args.split == "small":
        # Small subset for quick testing
        task_ids = split_data["train"][:5]
    else:
        raise ValueError(f"Unknown split: {args.split}")

    # Determine agents to evaluate
    if args.agent == "both":
        agents = ["amplifier", "baseline"]
    else:
        agents = [args.agent]

    # Run evaluation for each agent
    all_results = {}
    for agent in agents:
        print(f"\n{'='*60}")
        print(f"  EVALUATING: {agent.upper()} AGENT")
        print(f"{'='*60}\n")

        run_id = f"{agent}_{args.split}_{datetime.now().strftime('%Y-%m-%d__%H-%M-%S')}"

        try:
            # Run evaluation
            results = run_evaluation(
                agent=agent,
                task_ids=task_ids,
                output_dir=output_dir,
                run_id=run_id,
                n_concurrent_trials=args.concurrent,
                n_attempts=args.attempts,
                timeout_multiplier=args.timeout_multiplier,
                model_name=args.model
            )

            # Analyze results
            analysis = analyze_results(results)

            # Print summary first (so we see it even if save fails)
            print_summary(analysis)

            # Try to save results
            results_file = output_dir / f"{run_id}_results.json"
            try:
                save_results(results, analysis, results_file)
            except Exception as save_error:
                print(f"\n⚠️ Warning: Could not save results to JSON: {save_error}")
                # Try to at least save the analysis
                try:
                    with results_file.open("w") as f:
                        json.dump({"timestamp": datetime.now().isoformat(), "analysis": analysis}, f, indent=2)
                    print(f"💾 Analysis saved to: {results_file}")
                except:
                    print("⚠️ Could not save analysis either")

            all_results[agent] = {
                "results": results,
                "analysis": analysis,
                "output_dir": str(output_dir / run_id)
            }

        except Exception as e:
            print(f"\n❌ Error running evaluation for {agent}: {e}")
            import traceback
            traceback.print_exc()

            # Try to read results.json from the run directory if it exists
            run_dir = output_dir / run_id
            results_json = run_dir / "results.json"
            if results_json.exists():
                print("\n📊 Reading results from Terminal-Bench output...")
                try:
                    with results_json.open() as f:
                        tb_results = json.load(f)
                    # Analyze the terminal-bench results
                    tb_analysis = {
                        "total_tasks": len(tb_results.get("results", [])),
                        "successful": sum(1 for r in tb_results.get("results", []) if r.get("is_resolved", False)),
                        "failed": 0,
                        "success_rate": 0,
                        "failure_types": {}
                    }
                    tb_analysis["failed"] = tb_analysis["total_tasks"] - tb_analysis["successful"]
                    if tb_analysis["total_tasks"] > 0:
                        tb_analysis["success_rate"] = (tb_analysis["successful"] / tb_analysis["total_tasks"]) * 100

                    # Get failure details
                    for r in tb_results.get("results", []):
                        if not r.get("is_resolved", False):
                            task_id = r.get("task_id", "unknown")
                            tb_analysis["failure_types"][task_id] = "Task failed"

                    print_summary(tb_analysis)
                except Exception as read_error:
                    print(f"⚠️ Could not read Terminal-Bench results: {read_error}")

    # Compare results if both agents were run
    if len(all_results) == 2:
        print("\n" + "=" * 60)
        print("  COMPARISON: AMPLIFIER vs BASELINE")
        print("=" * 60)

        amp_analysis = all_results.get("amplifier", {}).get("analysis", {})
        base_analysis = all_results.get("baseline", {}).get("analysis", {})

        if amp_analysis and base_analysis:
            print(f"\nAmplifier success rate: {amp_analysis['success_rate']:.1f}%")
            print(f"Baseline success rate:  {base_analysis['success_rate']:.1f}%")

            improvement = amp_analysis['success_rate'] - base_analysis['success_rate']
            if improvement > 0:
                print(f"\n✅ Amplifier outperforms baseline by {improvement:.1f}%")
            elif improvement < 0:
                print(f"\n⚠️  Baseline outperforms amplifier by {-improvement:.1f}%")
            else:
                print(f"\n➖ Both agents have the same performance")

    print("\n✅ Evaluation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())