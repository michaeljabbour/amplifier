#!/usr/bin/env python3
"""
Run all task tests locally to verify the framework.
"""

import subprocess
import sys
from pathlib import Path
import time

def run_task_tests(task_name):
    """Run tests for a single task."""
    task_dir = Path(__file__).parent / 'tasks' / task_name
    test_file = task_dir / 'tests' / 'test_outputs.py'

    if not test_file.exists():
        return None, f"No tests found"

    start_time = time.time()
    try:
        result = subprocess.run(
            ['uv', 'run', 'pytest', str(test_file), '-q'],
            capture_output=True, text=True, timeout=30, cwd=task_dir
        )

        elapsed = time.time() - start_time

        # Parse pytest output
        if result.returncode == 0:
            # Extract test count from output like "5 passed in 1.04s"
            lines = result.stdout.split('\n')
            for line in lines:
                if 'passed' in line:
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        return True, f"{parts[0]} tests passed ({elapsed:.2f}s)"
            return True, f"Tests passed ({elapsed:.2f}s)"
        else:
            # Extract failure info
            if 'failed' in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'failed' in line:
                        return False, line.strip()
            return False, f"Tests failed (exit code {result.returncode})"

    except subprocess.TimeoutExpired:
        return False, "Timeout (>30s)"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Run all task tests."""
    tasks = [
        'fibonacci-calculator',
        'tree-traversal-master',
        'n-queens-solver',
        'tower-of-hanoi-solver',
        'nested-logic-resolver',
        'recursive-planner',
        'recursive-summarizer',
        'self-referential-solver',
        'recursive-agent-loop',
        # Skip contact-manager-api as it requires a server
    ]

    print("🧪 Running All Task Tests")
    print("=" * 60)

    passed = 0
    failed = 0
    skipped = 0

    for task in tasks:
        print(f"\n📦 {task}")
        success, message = run_task_tests(task)

        if success is None:
            print(f"   ⚠️  SKIP: {message}")
            skipped += 1
        elif success:
            print(f"   ✅ PASS: {message}")
            passed += 1
        else:
            print(f"   ❌ FAIL: {message}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\n📊 Summary:")
    print(f"   ✅ Passed: {passed}/{len(tasks)}")
    if failed > 0:
        print(f"   ❌ Failed: {failed}")
    if skipped > 0:
        print(f"   ⚠️  Skipped: {skipped}")

    success_rate = (passed / len(tasks)) * 100 if tasks else 0
    print(f"\n   Success Rate: {success_rate:.1f}%")

    if failed == 0:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} tasks have failing tests")
        sys.exit(1)

if __name__ == '__main__':
    main()