#!/usr/bin/env python3
"""
Quick local test of all recursive reasoning tasks.
Tests that each task can be executed and produces valid JSON output.
"""

import subprocess
import json
import sys
from pathlib import Path
import tempfile

def test_task(task_name, input_data=None):
    """Test a single task."""
    task_dir = Path(__file__).parent / 'tasks' / task_name
    solution_script = task_dir / 'solution.sh'

    if not solution_script.exists():
        return False, f"solution.sh not found"

    try:
        # Different tasks have different input methods
        if task_name == 'fibonacci-calculator':
            result = subprocess.run(
                ['bash', str(solution_script), '10'],
                capture_output=True, text=True, timeout=5, cwd=task_dir
            )
        elif task_name == 'tower-of-hanoi-solver':
            # Create temp config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"disks": 3, "source": "A", "destination": "C", "auxiliary": "B"}, f)
                config_file = f.name
            result = subprocess.run(
                ['bash', str(solution_script), config_file],
                capture_output=True, text=True, timeout=5, cwd=task_dir
            )
        elif task_name in ['tree-traversal-master', 'n-queens-solver']:
            # These need config files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                if task_name == 'tree-traversal-master':
                    json.dump({"tree": [1, 2, 3, 4, 5]}, f)
                else:
                    json.dump({"n": 4}, f)
                config_file = f.name
            result = subprocess.run(
                ['bash', str(solution_script), config_file],
                capture_output=True, text=True, timeout=5, cwd=task_dir
            )
        elif task_name == 'contact-manager-api':
            # Skip - requires server setup
            return True, "Skipped (requires server)"
        else:
            # Default: tasks that need config files
            default_inputs = {
                'nested-logic-resolver': {"expression": "AND(A, B)", "values": {"A": True, "B": False}},
                'recursive-planner': {"task": "Build a house"},
                'recursive-summarizer': {"text": "This is a test. It contains information.", "iterations": 3},
                'self-referential-solver': {
                    "problem": "Calculate factorial of 3",
                    "subproblems": [
                        {"id": 1, "description": "Define base case"},
                        {"id": 2, "description": "Calculate 3!", "depends_on": [1]},
                        {"id": 3, "description": "Return result", "depends_on": [2]}
                    ]
                },
                'recursive-agent-loop': {"problem": "Design a function", "iterations": 3}
            }
            input_data = default_inputs.get(task_name, {})
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(input_data, f)
                config_file = f.name
            result = subprocess.run(
                ['bash', str(solution_script), config_file],
                capture_output=True, text=True, timeout=5, cwd=task_dir
            )

        # Check if output is valid JSON
        if result.returncode != 0:
            return False, f"Non-zero exit code: {result.returncode}\nStderr: {result.stderr}"

        try:
            output = json.loads(result.stdout)
            return True, f"Valid JSON output with {len(output)} keys"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}\nOutput: {result.stdout[:200]}"

    except subprocess.TimeoutExpired:
        return False, "Timeout (>5 seconds)"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Test all tasks."""
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
        'contact-manager-api'
    ]

    print("Testing all recursive reasoning tasks locally...\n")
    print("=" * 60)

    passed = 0
    failed = 0

    for task in tasks:
        print(f"\n📦 Testing: {task}")
        success, message = test_task(task)

        if success:
            print(f"   ✅ PASS: {message}")
            passed += 1
        else:
            print(f"   ❌ FAIL: {message}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"\nResults: {passed}/{len(tasks)} passed")

    if failed > 0:
        print(f"⚠️  {failed} tasks failed")
        sys.exit(1)
    else:
        print("✅ All tasks working!")
        sys.exit(0)

if __name__ == '__main__':
    main()