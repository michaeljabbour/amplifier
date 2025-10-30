from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile

def run_planner(config):
    """Run the planner and return parsed JSON output."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_file = f.name

    try:
        # Try Docker path first, fallback to local path
        solution_path = '/app/solution.sh'
        if not os.path.exists(solution_path):
            solution_path = os.path.join(os.path.dirname(__file__), '..', 'solution.sh')
            solution_path = os.path.abspath(solution_path)

        result = subprocess.run(
            [solution_path, config_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
        return json.loads(result.stdout)
    finally:
        os.unlink(config_file)

def test_planner_simple_task():
    """Test planning with a simple non-decomposable task."""
    config = {
        "task": "Write a report",
        "decomposable": False
    }
    output = run_planner(config)

    assert "execution_plan" in output, "Missing execution_plan"
    assert len(output["execution_plan"]) == 1, "Simple task should have 1 plan entry"
    assert output["execution_plan"][0]["task"] == "Write a report"

def test_planner_two_level():
    """Test planning with two-level task hierarchy."""
    config = {
        "task": "Build a house",
        "decomposable": True,
        "subtasks": [
            {"task": "Prepare foundation", "decomposable": False},
            {"task": "Build walls", "decomposable": False}
        ]
    }
    output = run_planner(config)

    assert "execution_plan" in output, "Missing execution_plan"
    assert output["total_tasks"] == 3, f"Expected 3 tasks, got {output['total_tasks']}"
    # Root task + 2 subtasks
    assert len(output["execution_plan"]) == 3, f"Expected 3 plan entries, got {len(output['execution_plan'])}"

def test_planner_three_level():
    """Test planning with three-level task hierarchy."""
    config = {
        "task": "Build a car",
        "decomposable": True,
        "subtasks": [
            {"task": "Build engine", "decomposable": True, "subtasks": [
                {"task": "Assemble cylinders", "decomposable": False},
                {"task": "Install pistons", "decomposable": False}
            ]},
            {"task": "Build frame", "decomposable": False}
        ]
    }
    output = run_planner(config)

    assert "execution_plan" in output, "Missing execution_plan"
    # Root + 2 subtasks + 2 sub-subtasks = 5 total
    assert output["total_tasks"] == 5, f"Expected 5 tasks, got {output['total_tasks']}"

def test_planner_max_depth():
    """Test that max_depth is calculated correctly."""
    config = {
        "task": "Build a car",
        "decomposable": True,
        "subtasks": [
            {"task": "Build engine", "decomposable": True, "subtasks": [
                {"task": "Assemble cylinders", "decomposable": False},
                {"task": "Install pistons", "decomposable": False}
            ]},
            {"task": "Build frame", "decomposable": False}
        ]
    }
    output = run_planner(config)

    assert "max_depth" in output, "Missing max_depth"
    assert output["max_depth"] > 0, "max_depth should be positive"
    # Three-level hierarchy: root (1), subtask (2), sub-subtask (3)
    assert output["max_depth"] == 3, f"Expected max_depth=3, got {output['max_depth']}"

def test_planner_recursion_depth():
    """Test that recursion depth is tracked."""
    config = {
        "task": "Build a house",
        "decomposable": True,
        "subtasks": [
            {"task": "Prepare foundation", "decomposable": False},
            {"task": "Build structure", "decomposable": True, "subtasks": [
                {"task": "Frame walls", "decomposable": False},
                {"task": "Install roof", "decomposable": False}
            ]}
        ]
    }
    output = run_planner(config)

    assert "recursion_depth" in output, "Missing recursion_depth"
    assert output["recursion_depth"] > 0, "recursion_depth should be positive"

def test_planner_task_ids():
    """Test that task IDs are unique and sequential."""
    config = {
        "task": "Build a house",
        "decomposable": True,
        "subtasks": [
            {"task": "Foundation", "decomposable": False},
            {"task": "Walls", "decomposable": False},
            {"task": "Roof", "decomposable": False}
        ]
    }
    output = run_planner(config)

    task_ids = [entry["id"] for entry in output["execution_plan"]]
    # IDs should be unique
    assert len(task_ids) == len(set(task_ids)), "Task IDs should be unique"
    # Should have 4 tasks (root + 3 subtasks)
    assert len(task_ids) == 4, f"Expected 4 tasks, got {len(task_ids)}"

def test_planner_subtask_references():
    """Test that subtask references are correct."""
    config = {
        "task": "Build a house",
        "decomposable": True,
        "subtasks": [
            {"task": "Foundation", "decomposable": False},
            {"task": "Walls", "decomposable": False}
        ]
    }
    output = run_planner(config)

    # Find the root task (it should reference the two subtasks)
    root = None
    for entry in output["execution_plan"]:
        if entry["task"] == "Build a house":
            root = entry
            break

    assert root is not None, "Root task not found"
    assert len(root["subtasks"]) == 2, f"Root should have 2 subtasks, got {len(root['subtasks'])}"

def test_planner_execution_time():
    """Test that execution time is recorded."""
    config = {
        "task": "Simple task",
        "decomposable": False
    }
    output = run_planner(config)

    assert "execution_time_ms" in output, "Missing execution_time_ms"
    assert isinstance(output["execution_time_ms"], (int, float)), \
        f"execution_time_ms should be numeric, got {type(output['execution_time_ms'])}"
    assert output["execution_time_ms"] >= 0, "execution_time_ms should be non-negative"

def test_planner_json_format():
    """Test that output is valid JSON with expected fields."""
    config = {
        "task": "Simple task",
        "decomposable": False
    }
    output = run_planner(config)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "original_task" in output, "Missing original_task"
    assert "execution_plan" in output, "Missing execution_plan"
    assert "total_tasks" in output, "Missing total_tasks"
    assert "max_depth" in output, "Missing max_depth"
    assert "recursion_depth" in output, "Missing recursion_depth"
    assert "execution_time_ms" in output, "Missing execution_time_ms"

def test_planner_plan_entry_structure():
    """Test that plan entries have correct structure."""
    config = {
        "task": "Build a house",
        "decomposable": True,
        "subtasks": [
            {"task": "Foundation", "decomposable": False}
        ]
    }
    output = run_planner(config)

    for entry in output["execution_plan"]:
        assert "id" in entry, "Plan entry missing id"
        assert "task" in entry, "Plan entry missing task"
        assert "subtasks" in entry, "Plan entry missing subtasks"
        assert "depth" in entry, "Plan entry missing depth"
        assert isinstance(entry["id"], str), "id should be string"
        assert isinstance(entry["task"], str), "task should be string"
        assert isinstance(entry["subtasks"], list), "subtasks should be list"
        assert isinstance(entry["depth"], int), "depth should be integer"

def test_planner_invalid_config():
    """Test error handling for invalid configs."""
    # Missing task field
    config = {"decomposable": False}
    output = run_planner(config)
    assert "error" in output, "Should error for missing task"

    # Invalid decomposable type
    config = {"task": "Test", "decomposable": "true"}
    output = run_planner(config)
    assert "error" in output, "Should error for invalid decomposable type"

    # Invalid subtasks type
    config = {"task": "Test", "decomposable": True, "subtasks": "invalid"}
    output = run_planner(config)
    assert "error" in output, "Should error for invalid subtasks type"

def test_planner_empty_subtasks():
    """Test handling of empty subtasks list."""
    config = {
        "task": "Main task",
        "decomposable": True,
        "subtasks": []
    }
    output = run_planner(config)

    assert "execution_plan" in output, "Should handle empty subtasks"
    # Empty subtasks means the task is treated as leaf
    assert output["total_tasks"] >= 1, "Should have at least the root task"

def test_planner_deeply_nested():
    """Test deeply nested task hierarchy."""
    config = {
        "task": "Level 1",
        "decomposable": True,
        "subtasks": [
            {
                "task": "Level 2",
                "decomposable": True,
                "subtasks": [
                    {
                        "task": "Level 3",
                        "decomposable": True,
                        "subtasks": [
                            {
                                "task": "Level 4",
                                "decomposable": False
                            }
                        ]
                    }
                ]
            }
        ]
    }
    output = run_planner(config)

    assert output["max_depth"] == 4, f"Expected max_depth=4, got {output['max_depth']}"
    assert output["total_tasks"] == 4, f"Expected 4 tasks, got {output['total_tasks']}"

if __name__ == "__main__":
    test_planner_simple_task()
    test_planner_two_level()
    test_planner_three_level()
    test_planner_max_depth()
    test_planner_recursion_depth()
    test_planner_task_ids()
    test_planner_subtask_references()
    test_planner_execution_time()
    test_planner_json_format()
    test_planner_plan_entry_structure()
    test_planner_invalid_config()
    test_planner_empty_subtasks()
    test_planner_deeply_nested()
    print("All tests passed!")
