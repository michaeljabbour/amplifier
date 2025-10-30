#!/usr/bin/env python3
"""
Analyze the last Terminal-Bench evaluation run.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def find_latest_run():
    """Find the most recent run directory."""
    base_dir = Path("/Users/michaeljabbour/dev/ai_working/tmp")
    if not base_dir.exists():
        return None

    # Find all amplifier run directories
    run_dirs = [d for d in base_dir.glob("amplifier_*") if d.is_dir()]
    if not run_dirs:
        return None

    # Sort by modification time and get the latest
    return max(run_dirs, key=lambda x: x.stat().st_mtime)

def analyze_run(run_dir):
    """Analyze a specific run."""
    results_file = run_dir / "results.json"
    if not results_file.exists():
        print(f"❌ No results.json found in {run_dir}")
        return

    with open(results_file) as f:
        data = json.load(f)

    results = data.get('results', [])

    print(f"📊 Terminal-Bench Evaluation Results")
    print(f"📁 Run: {run_dir.name}")
    print("=" * 60)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.get('is_resolved', False))
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{total}")
    print("\n" + "=" * 60)
    print("\nDetailed Results:")
    print("-" * 60)

    for r in results:
        status = '✅' if r.get('is_resolved', False) else '❌'
        task = r.get('task_id', 'unknown')

        # Calculate duration
        if r.get('agent_started_at') and r.get('agent_ended_at'):
            start = datetime.fromisoformat(r['agent_started_at'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(r['agent_ended_at'].replace('Z', '+00:00'))
            duration = (end - start).total_seconds()
            duration_str = f"{duration:.1f}s"
        else:
            duration_str = "N/A"

        print(f"\n{status} {task}")
        print(f"   Duration: {duration_str}")

        # Show test results
        if 'parser_results' in r:
            tests = r['parser_results']
            passed_tests = sum(1 for v in tests.values() if v == 'passed')
            total_tests = len(tests)
            print(f"   Tests: {passed_tests}/{total_tests} passed")

            # Show failed tests
            failed_tests = [k for k, v in tests.items() if v != 'passed']
            if failed_tests:
                print(f"   Failed: {', '.join(failed_tests)}")

    print("\n" + "=" * 60)

    # Performance Summary
    print("\n📈 Performance Summary:")
    print("-" * 60)

    # Calculate average duration for successful tasks
    successful_durations = []
    for r in results:
        if r.get('is_resolved') and r.get('agent_started_at') and r.get('agent_ended_at'):
            start = datetime.fromisoformat(r['agent_started_at'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(r['agent_ended_at'].replace('Z', '+00:00'))
            successful_durations.append((end - start).total_seconds())

    if successful_durations:
        avg_duration = sum(successful_durations) / len(successful_durations)
        print(f"Average successful task duration: {avg_duration:.1f}s")
        print(f"Fastest task: {min(successful_durations):.1f}s")
        print(f"Slowest task: {max(successful_durations):.1f}s")

    print("\n" + "=" * 60)
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("🏆 Excellent performance!")
    elif success_rate >= 60:
        print("👍 Good performance!")
    elif success_rate >= 40:
        print("🔧 Needs improvement")
    else:
        print("⚠️  Significant issues to address")

def main():
    """Main entry point."""
    # Check if a specific run directory was provided
    import sys
    if len(sys.argv) > 1:
        run_dir = Path(sys.argv[1])
    else:
        run_dir = find_latest_run()

    if not run_dir or not run_dir.exists():
        print("❌ No evaluation runs found")
        return

    analyze_run(run_dir)

if __name__ == "__main__":
    main()