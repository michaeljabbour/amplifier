#!/usr/bin/env python3
"""
Monitor a running terminal-bench evaluation and provide real-time progress updates.
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def find_latest_run(base_dir: Path, agent_filter: str = None) -> Path | None:
    """Find the latest run directory."""
    run_dirs = []

    for dir_path in base_dir.iterdir():
        if not dir_path.is_dir():
            continue

        # Filter by agent if specified
        if agent_filter and agent_filter not in dir_path.name:
            continue

        # Check if it looks like a run directory
        if "__" in dir_path.name:
            run_dirs.append(dir_path)

    if not run_dirs:
        return None

    # Return the most recent based on directory name
    return sorted(run_dirs, reverse=True)[0]


def get_run_status(run_dir: Path) -> Dict[str, Any]:
    """Get the current status of a run."""
    status = {
        "run_id": run_dir.name,
        "tasks": {},
        "summary": {
            "total": 0,
            "completed": 0,
            "successful": 0,
            "failed": 0,
            "in_progress": 0,
            "pending": 0
        }
    }

    # Check for results.json (final results)
    results_file = run_dir / "results.json"
    if results_file.exists():
        with results_file.open() as f:
            results = json.load(f)

        for result in results.get("results", []):
            task_id = result.get("task_id")
            success = result.get("success", False)

            status["tasks"][task_id] = {
                "status": "success" if success else "failed",
                "completed": True
            }

            status["summary"]["total"] += 1
            status["summary"]["completed"] += 1
            if success:
                status["summary"]["successful"] += 1
            else:
                status["summary"]["failed"] += 1

    # Check individual task directories for in-progress tasks
    for task_dir in run_dir.iterdir():
        if not task_dir.is_dir():
            continue

        task_id = task_dir.name

        # Skip if already in results
        if task_id in status["tasks"]:
            continue

        # Check for session directories (indicates task started)
        sessions = list(task_dir.glob("*/sessions"))
        if sessions:
            # Check for agent.log to see if it's still running
            agent_logs = list(task_dir.glob("*/sessions/agent.log"))
            if agent_logs:
                status["tasks"][task_id] = {
                    "status": "in_progress",
                    "completed": False
                }
                status["summary"]["in_progress"] += 1
            else:
                status["tasks"][task_id] = {
                    "status": "starting",
                    "completed": False
                }
                status["summary"]["in_progress"] += 1
        else:
            status["tasks"][task_id] = {
                "status": "pending",
                "completed": False
            }
            status["summary"]["pending"] += 1

        status["summary"]["total"] += 1

    return status


def print_status(status: Dict[str, Any], clear: bool = True) -> None:
    """Print the current status."""
    if clear:
        print("\033[2J\033[H")  # Clear screen

    print("=" * 60)
    print(f"📊 TERMINAL-BENCH EVALUATION MONITOR")
    print(f"🏃 Run ID: {status['run_id']}")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    summary = status["summary"]
    total = summary["total"]
    completed = summary["completed"]

    if total > 0:
        progress = completed / total * 100

        # Progress bar
        bar_width = 40
        filled = int(bar_width * completed / total)
        bar = "█" * filled + "░" * (bar_width - filled)

        print(f"\nProgress: [{bar}] {progress:.1f}%")
        print(f"         {completed}/{total} tasks completed")

    print("\n📈 Status Summary:")
    print(f"  ✅ Successful:  {summary['successful']:3d}")
    print(f"  ❌ Failed:      {summary['failed']:3d}")
    print(f"  🔄 In Progress: {summary['in_progress']:3d}")
    print(f"  ⏳ Pending:     {summary['pending']:3d}")
    print(f"  ───────────────────")
    print(f"  📝 Total:       {summary['total']:3d}")

    if summary['completed'] > 0:
        success_rate = summary['successful'] / summary['completed'] * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}% "
              f"({summary['successful']}/{summary['completed']})")

    # Show recent activity
    in_progress_tasks = [
        task_id for task_id, info in status["tasks"].items()
        if info["status"] == "in_progress"
    ]

    if in_progress_tasks:
        print(f"\n🔄 Currently Running ({len(in_progress_tasks)}):")
        for task_id in in_progress_tasks[:5]:
            print(f"  - {task_id}")
        if len(in_progress_tasks) > 5:
            print(f"  ... and {len(in_progress_tasks) - 5} more")

    # Show recent failures
    failed_tasks = [
        task_id for task_id, info in status["tasks"].items()
        if info.get("status") == "failed"
    ]

    if failed_tasks:
        print(f"\n❌ Failed Tasks ({len(failed_tasks)}):")
        for task_id in failed_tasks[:5]:
            print(f"  - {task_id}")
        if len(failed_tasks) > 5:
            print(f"  ... and {len(failed_tasks) - 5} more")


def monitor_loop(
    run_dir: Path,
    refresh_interval: int = 5,
    clear_screen: bool = True
) -> None:
    """Monitor a run in a loop."""
    print(f"📁 Monitoring: {run_dir}")
    print(f"🔄 Refresh interval: {refresh_interval} seconds")
    print("Press Ctrl+C to stop monitoring\n")

    try:
        while True:
            status = get_run_status(run_dir)
            print_status(status, clear=clear_screen)

            # Check if evaluation is complete
            summary = status["summary"]
            if summary["completed"] == summary["total"] and summary["total"] > 0:
                print("\n✅ Evaluation Complete!")
                break

            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor a running terminal-bench evaluation"
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="Specific run directory to monitor"
    )
    parser.add_argument(
        "--agent",
        choices=["amplifier", "baseline"],
        help="Filter for specific agent type when finding latest run"
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't clear screen between updates"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Show status once and exit"
    )

    args = parser.parse_args()

    # Find run directory
    if args.run_dir:
        run_dir = args.run_dir
    else:
        base_dir = Path(__file__).parents[2] / "ai_working" / "tmp"
        run_dir = find_latest_run(base_dir, args.agent)

        if not run_dir:
            print(f"❌ No run directories found in {base_dir}")
            if args.agent:
                print(f"   (filtered for agent: {args.agent})")
            return 1

    # Verify run directory exists
    if not run_dir.exists():
        print(f"❌ Run directory not found: {run_dir}")
        return 1

    # Get and display status
    if args.once:
        status = get_run_status(run_dir)
        print_status(status, clear=False)
    else:
        monitor_loop(
            run_dir,
            refresh_interval=args.refresh,
            clear_screen=not args.no_clear
        )

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())