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

from terminal_bench import Harness


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

    # Configure agent import path
    if agent == "amplifier":
        agent_import_path = "custom_agents:CustomAmplifierAgent"
    elif agent == "baseline":
        agent_import_path = "custom_agents:ClaudeCodeAgent"
    else:
        raise ValueError(f"Unknown agent type: {agent}")

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

    # Initialize harness
    harness_kwargs = {
        "output_path": output_dir,
        "run_id": run_id,
        "dataset_name": "terminal-bench-core",
        "dataset_version": "0.1.1",
        "agent_import_path": agent_import_path,
        "no_rebuild": False,
        "cleanup": True,
        "task_ids": task_ids,
        "n_concurrent_trials": n_concurrent_trials,
        "n_attempts": n_attempts,
        "global_timeout_multiplier": timeout_multiplier,
    }

    if model_name:
        harness_kwargs["model_name"] = model_name

    harness = Harness(**harness_kwargs)

    # Run evaluation
    print("\n🏃 Running evaluation...")
    results = harness.run()

    return results


def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the evaluation results."""
    total = len(results)
    successful = sum(1 for r in results if r.get("success", False))
    failed = total - successful

    # Group failures by type
    failure_types = {}
    for result in results:
        if not result.get("success", False):
            task_id = result.get("task_id", "unknown")
            error = result.get("error", "unknown error")
            failure_types[task_id] = error[:200] if isinstance(error, str) else str(error)[:200]

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
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "raw_results": results
    }

    with output_file.open("w") as f:
        json.dump(output_data, f, indent=2)

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
        default=5,
        help="Number of concurrent trials (default: 5)"
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
        help="Output directory (default: ai_working/tmp)"
    )

    args = parser.parse_args()

    # Setup paths
    base_dir = Path(__file__).parents[2]
    split_file = Path(__file__).parent / "split.json"
    output_dir = args.output_dir or base_dir / "ai_working" / "tmp"
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

            # Save results
            results_file = output_dir / f"{run_id}_results.json"
            save_results(results, analysis, results_file)

            # Print summary
            print_summary(analysis)

            all_results[agent] = {
                "results": results,
                "analysis": analysis,
                "output_dir": str(output_dir / run_id)
            }

        except Exception as e:
            print(f"\n❌ Error running evaluation for {agent}: {e}")
            import traceback
            traceback.print_exc()

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