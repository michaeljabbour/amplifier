from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile

def run_solver(problem_spec):
    """Run the solver script and return parsed JSON output."""
    # Create a temporary problem file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(problem_spec, f)
        temp_file = f.name

    try:
        # Try Docker path first, then fallback to local path
        solution_path = '/app/solution.sh'
        if not os.path.exists(solution_path):
            solution_path = os.path.join(os.path.dirname(__file__), '..', 'solution.sh')

        result = subprocess.run(
            ['bash', solution_path, temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        return json.loads(result.stdout)
    finally:
        os.unlink(temp_file)

def test_basic_problem_solving():
    """Test basic problem decomposition and solving."""
    problem = {
        "problem": "Calculate the sum of squared even numbers",
        "subproblems": [
            {"id": 1, "description": "Parse input list"},
            {"id": 2, "description": "Filter even numbers", "depends_on": [1]},
            {"id": 3, "description": "Square each number", "depends_on": [2]},
            {"id": 4, "description": "Sum all squares", "depends_on": [3]}
        ]
    }

    output = run_solver(problem)

    assert "solution_chain" in output, "Missing solution_chain"
    assert len(output["solution_chain"]) == 4, f"Expected 4 solutions, got {len(output['solution_chain'])}"

    # Verify each solution step
    for i, step in enumerate(output["solution_chain"], 1):
        assert step["step"] == i, f"Step mismatch at index {i}"
        assert "subproblem" in step, f"Missing subproblem in step {i}"
        assert "solution" in step, f"Missing solution in step {i}"
        assert "depth" in step, f"Missing depth in step {i}"
        assert "dependencies" in step, f"Missing dependencies in step {i}"

def test_self_reference():
    """Test that solutions reference previous steps."""
    problem = {
        "problem": "Build incrementally",
        "subproblems": [
            {"id": 1, "description": "Step one"},
            {"id": 2, "description": "Step two", "depends_on": [1]},
            {"id": 3, "description": "Step three", "depends_on": [2]}
        ]
    }

    output = run_solver(problem)

    # Check that later steps reference earlier steps
    for i, step in enumerate(output["solution_chain"]):
        if step["dependencies"]:
            assert len(step["dependencies"]) > 0, f"Step {i+1} should have references"

def test_dependency_tracking():
    """Test that dependencies are tracked correctly."""
    problem = {
        "problem": "Complex dependencies",
        "subproblems": [
            {"id": 1, "description": "A"},
            {"id": 2, "description": "B"},
            {"id": 3, "description": "C", "depends_on": [1, 2]},
            {"id": 4, "description": "D", "depends_on": [3]},
            {"id": 5, "description": "E", "depends_on": [1, 4]}
        ]
    }

    output = run_solver(problem)

    assert "dependency_count" in output, "Missing dependency_count"
    assert output["dependency_count"] == 5, f"Expected 5 dependencies, got {output['dependency_count']}"

    # Verify total steps
    assert output["total_steps"] == 5, f"Expected 5 total steps, got {output['total_steps']}"

def test_max_depth_tracking():
    """Test that maximum depth is tracked correctly."""
    problem = {
        "problem": "Linear dependency chain",
        "subproblems": [
            {"id": 1, "description": "Level 1"},
            {"id": 2, "description": "Level 2", "depends_on": [1]},
            {"id": 3, "description": "Level 3", "depends_on": [2]},
            {"id": 4, "description": "Level 4", "depends_on": [3]},
            {"id": 5, "description": "Level 5", "depends_on": [4]}
        ]
    }

    output = run_solver(problem)

    assert "max_depth" in output, "Missing max_depth"
    assert output["max_depth"] == 5, f"Expected max_depth 5, got {output['max_depth']}"

def test_circular_dependency_error():
    """Test handling of circular dependencies."""
    problem = {
        "problem": "Invalid circular dependencies",
        "subproblems": [
            {"id": 1, "description": "A", "depends_on": [2]},
            {"id": 2, "description": "B", "depends_on": [1]}
        ]
    }

    output = run_solver(problem)
    assert "error" in output, "Should error for circular dependencies"

def test_no_subproblems_error():
    """Test error handling for missing subproblems."""
    problem = {
        "problem": "No decomposition"
    }

    output = run_solver(problem)
    assert "error" in output, "Should error for missing subproblems"

def test_missing_problem_field_error():
    """Test error handling for missing problem field."""
    problem = {
        "subproblems": [
            {"id": 1, "description": "A"}
        ]
    }

    output = run_solver(problem)
    assert "error" in output, "Should error for missing problem field"

def test_complex_dependency_graph():
    """Test with a more complex dependency structure."""
    problem = {
        "problem": "Multi-stage processing",
        "subproblems": [
            {"id": 1, "description": "Load data"},
            {"id": 2, "description": "Validate data", "depends_on": [1]},
            {"id": 3, "description": "Transform data", "depends_on": [2]},
            {"id": 4, "description": "Enrich data", "depends_on": [3]},
            {"id": 5, "description": "Cache results", "depends_on": [4]},
            {"id": 6, "description": "Index results", "depends_on": [5]},
            {"id": 7, "description": "Notify users", "depends_on": [6]}
        ]
    }

    output = run_solver(problem)

    assert output["total_steps"] == 7, f"Expected 7 steps, got {output['total_steps']}"
    assert output["max_depth"] == 7, f"Expected max_depth 7, got {output['max_depth']}"
    assert output["dependency_count"] == 6, f"Expected 6 dependencies, got {output['dependency_count']}"

def test_json_output_format():
    """Test that output is valid JSON with expected structure."""
    problem = {
        "problem": "Test format",
        "subproblems": [
            {"id": 1, "description": "Task 1"},
            {"id": 2, "description": "Task 2", "depends_on": [1]}
        ]
    }

    output = run_solver(problem)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "problem" in output, "Missing problem"
    assert "total_steps" in output, "Missing total_steps"
    assert "max_depth" in output, "Missing max_depth"
    assert "dependency_count" in output, "Missing dependency_count"
    assert "execution_time_ms" in output, "Missing execution_time_ms"

    # Verify types
    assert isinstance(output["total_steps"], int)
    assert isinstance(output["max_depth"], int)
    assert isinstance(output["dependency_count"], int)
    assert isinstance(output["execution_time_ms"], (int, float))

if __name__ == "__main__":
    test_basic_problem_solving()
    test_self_reference()
    test_dependency_tracking()
    test_max_depth_tracking()
    test_circular_dependency_error()
    test_no_subproblems_error()
    test_missing_problem_field_error()
    test_complex_dependency_graph()
    test_json_output_format()
    print("All tests passed!")
