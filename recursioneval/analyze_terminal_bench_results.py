#!/usr/bin/env python3
"""
Analyze Terminal-Bench evaluation results and generate summary.
Can be used to send results to AI for further analysis.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def find_latest_run(base_dir: Path = None) -> Path:
    """Find the most recent run directory."""
    if base_dir is None:
        base_dir = Path(__file__).parent / "results"

    if not base_dir.exists():
        return None

    # Find all amplifier run directories
    run_dirs = [d for d in base_dir.glob("amplifier_*") if d.is_dir()]
    if not run_dirs:
        return None

    # Sort by modification time and get the latest
    return max(run_dirs, key=lambda x: x.stat().st_mtime)


def analyze_terminal_bench_results(run_dir: Path) -> Dict[str, Any]:
    """Analyze Terminal-Bench results.json file."""
    results_file = run_dir / "results.json"

    if not results_file.exists():
        return {"error": f"No results.json found in {run_dir}"}

    with open(results_file) as f:
        data = json.load(f)

    results = data.get('results', [])

    # Calculate metrics
    total = len(results)
    passed = sum(1 for r in results if r.get('is_resolved', False))
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    # Categorize tasks
    passed_tasks = []
    failed_tasks = []

    for r in results:
        task_info = {
            'task_id': r.get('task_id', 'unknown'),
            'duration': None,
            'tests': {}
        }

        # Calculate duration
        if r.get('agent_started_at') and r.get('agent_ended_at'):
            start = datetime.fromisoformat(r['agent_started_at'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(r['agent_ended_at'].replace('Z', '+00:00'))
            task_info['duration'] = (end - start).total_seconds()

        # Get test results
        if 'parser_results' in r and r['parser_results'] is not None:
            task_info['tests'] = r['parser_results']
            task_info['tests_passed'] = sum(1 for v in r['parser_results'].values() if v == 'passed')
            task_info['tests_total'] = len(r['parser_results'])

        if r.get('is_resolved', False):
            passed_tasks.append(task_info)
        else:
            failed_tasks.append(task_info)

    # Calculate average durations
    successful_durations = [t['duration'] for t in passed_tasks if t['duration']]
    failed_durations = [t['duration'] for t in failed_tasks if t['duration']]

    avg_success_duration = sum(successful_durations) / len(successful_durations) if successful_durations else 0
    avg_failed_duration = sum(failed_durations) / len(failed_durations) if failed_durations else 0

    return {
        'run_id': run_dir.name,
        'total_tasks': total,
        'passed': passed,
        'failed': failed,
        'success_rate': success_rate,
        'passed_tasks': passed_tasks,
        'failed_tasks': failed_tasks,
        'avg_success_duration': avg_success_duration,
        'avg_failed_duration': avg_failed_duration,
        'fastest_task': min(successful_durations) if successful_durations else 0,
        'slowest_task': max(successful_durations) if successful_durations else 0
    }


def generate_summary(analysis: Dict[str, Any]) -> str:
    """Generate a human-readable summary."""
    lines = []
    lines.append("# Terminal-Bench Evaluation Results Summary\n")
    lines.append(f"**Run ID:** {analysis['run_id']}")
    lines.append(f"**Success Rate:** {analysis['success_rate']:.1f}% ({analysis['passed']}/{analysis['total_tasks']} tasks passed)\n")

    lines.append("## Performance Metrics")
    if analysis['avg_success_duration'] > 0:
        lines.append(f"- Average successful task duration: {analysis['avg_success_duration']:.1f}s")
        lines.append(f"- Fastest task: {analysis['fastest_task']:.1f}s")
        lines.append(f"- Slowest task: {analysis['slowest_task']:.1f}s")
    if analysis['avg_failed_duration'] > 0:
        lines.append(f"- Average failed task duration: {analysis['avg_failed_duration']:.1f}s")
    lines.append("")

    lines.append("## Passed Tasks")
    if analysis['passed_tasks']:
        for task in analysis['passed_tasks']:
            duration_str = f"{task['duration']:.1f}s" if task['duration'] else "N/A"
            test_str = f"{task.get('tests_passed', 0)}/{task.get('tests_total', 0)} tests" if task.get('tests_total', 0) > 0 else ""
            lines.append(f"✅ **{task['task_id']}** - {duration_str} - {test_str}")
    else:
        lines.append("None")
    lines.append("")

    lines.append("## Failed Tasks")
    if analysis['failed_tasks']:
        for task in analysis['failed_tasks']:
            duration_str = f"{task['duration']:.1f}s" if task['duration'] else "N/A"
            test_str = f"{task.get('tests_passed', 0)}/{task.get('tests_total', 0)} tests passed" if task.get('tests_total', 0) > 0 else "no tests run"
            lines.append(f"❌ **{task['task_id']}** - {duration_str} - {test_str}")

            # Show which tests failed
            if task.get('tests'):
                failed_tests = [k for k, v in task['tests'].items() if v != 'passed']
                if failed_tests:
                    lines.append(f"   Failed tests: {', '.join(failed_tests)}")
    else:
        lines.append("None")
    lines.append("")

    # Add recommendations
    lines.append("## Analysis")
    if analysis['success_rate'] >= 80:
        lines.append("🏆 Excellent performance! The agent successfully completed most tasks.")
    elif analysis['success_rate'] >= 60:
        lines.append("👍 Good performance with room for improvement.")
    elif analysis['success_rate'] >= 40:
        lines.append("🔧 Moderate performance. Several tasks need attention.")
    else:
        lines.append("⚠️ Low success rate indicates significant issues to address.")

    if analysis['failed_tasks']:
        lines.append("\n### Failure Analysis")
        # Group failures by common patterns
        test_failures = {}
        for task in analysis['failed_tasks']:
            if task.get('tests'):
                for test, result in task['tests'].items():
                    if result != 'passed':
                        if test not in test_failures:
                            test_failures[test] = []
                        test_failures[test].append(task['task_id'])

        if test_failures:
            lines.append("Common test failures:")
            for test, tasks in test_failures.items():
                lines.append(f"- **{test}** failed in: {', '.join(tasks[:5])}")
                if len(tasks) > 5:
                    lines.append(f"  ... and {len(tasks)-5} more tasks")

    return "\n".join(lines)


def generate_json_for_ai(analysis: Dict[str, Any]) -> str:
    """Generate a JSON summary optimized for AI analysis."""
    ai_summary = {
        "evaluation_summary": {
            "run_id": analysis['run_id'],
            "success_rate": analysis['success_rate'],
            "total_tasks": analysis['total_tasks'],
            "passed": analysis['passed'],
            "failed": analysis['failed']
        },
        "performance": {
            "avg_success_duration_seconds": round(analysis['avg_success_duration'], 1),
            "avg_failed_duration_seconds": round(analysis['avg_failed_duration'], 1),
            "fastest_task_seconds": round(analysis['fastest_task'], 1),
            "slowest_task_seconds": round(analysis['slowest_task'], 1)
        },
        "task_details": {
            "passed": [
                {
                    "id": t['task_id'],
                    "duration": round(t['duration'], 1) if t['duration'] else None,
                    "test_pass_rate": f"{t.get('tests_passed', 0)}/{t.get('tests_total', 0)}"
                }
                for t in analysis['passed_tasks']
            ],
            "failed": [
                {
                    "id": t['task_id'],
                    "duration": round(t['duration'], 1) if t['duration'] else None,
                    "test_pass_rate": f"{t.get('tests_passed', 0)}/{t.get('tests_total', 0)}",
                    "failed_tests": [k for k, v in t.get('tests', {}).items() if v != 'passed']
                }
                for t in analysis['failed_tasks']
            ]
        },
        "recommendations": []
    }

    # Add recommendations based on analysis
    if analysis['success_rate'] < 50:
        ai_summary["recommendations"].append("Investigate common failure patterns across tasks")
    if analysis['avg_failed_duration'] > analysis['avg_success_duration'] * 2:
        ai_summary["recommendations"].append("Failed tasks taking much longer - may indicate timeout issues")
    if any(t.get('tests_total', 0) == 0 for t in analysis['failed_tasks']):
        ai_summary["recommendations"].append("Some tasks failed before running tests - check agent initialization")

    return json.dumps(ai_summary, indent=2)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Analyze Terminal-Bench results")
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Specific run directory to analyze"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "both"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: stdout)"
    )

    args = parser.parse_args()

    # Find run directory
    if args.run_dir:
        run_dir = args.run_dir
    else:
        run_dir = find_latest_run()

    if not run_dir or not run_dir.exists():
        print("❌ No evaluation runs found", file=sys.stderr)
        return 1

    # Analyze results
    analysis = analyze_terminal_bench_results(run_dir)

    if "error" in analysis:
        print(f"❌ {analysis['error']}", file=sys.stderr)
        return 1

    # Generate output
    if args.format == "text" or args.format == "both":
        summary = generate_summary(analysis)
        if args.output and args.format == "text":
            with open(args.output, "w") as f:
                f.write(summary)
            print(f"📝 Summary saved to: {args.output}")
        else:
            print(summary)

    if args.format == "json" or args.format == "both":
        json_summary = generate_json_for_ai(analysis)
        if args.format == "both":
            print("\n" + "="*60 + "\n")
            print("JSON Summary for AI Analysis:")
            print("="*60 + "\n")

        if args.output and args.format == "json":
            with open(args.output, "w") as f:
                f.write(json_summary)
            print(f"📝 JSON saved to: {args.output}")
        else:
            print(json_summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())