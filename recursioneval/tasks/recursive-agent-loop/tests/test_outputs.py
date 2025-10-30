from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile

def run_agent_loop(problem, iterations=5):
    """Run the agent loop script and return parsed JSON output."""
    # Create a temporary problem file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(problem)
        temp_file = f.name

    try:
        # Try Docker path first, then fallback to local path
        solution_path = '/app/solution.sh'
        if not os.path.exists(solution_path):
            solution_path = os.path.join(os.path.dirname(__file__), '..', 'solution.sh')

        result = subprocess.run(
            ['bash', solution_path, temp_file, str(iterations)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return json.loads(result.stdout)
    finally:
        os.unlink(temp_file)

def test_basic_self_improvement():
    """Test basic self-improving agent loop."""
    problem = "Design an efficient sorting algorithm for large datasets"

    output = run_agent_loop(problem, iterations=3)

    assert "problem" in output, "Missing problem"
    assert "solutions" in output, "Missing solutions"
    assert len(output["solutions"]) == 3, f"Expected 3 solutions, got {len(output['solutions'])}"

    # Check each solution
    for i, solution in enumerate(output["solutions"], 1):
        assert solution["iteration"] == i, f"Iteration mismatch at index {i}"
        assert "solution" in solution, f"Missing solution in iteration {i}"
        assert "quality_score" in solution, f"Missing quality_score in iteration {i}"
        assert "improvement" in solution, f"Missing improvement in iteration {i}"
        assert 0 <= solution["quality_score"] <= 1, f"Quality score out of range: {solution['quality_score']}"

def test_quality_progression():
    """Test that quality scores generally increase."""
    problem = "Implement a distributed cache with consistency guarantees"

    output = run_agent_loop(problem, iterations=5)

    quality_scores = [s["quality_score"] for s in output["solutions"]]

    # Quality should generally not decrease
    for i in range(1, len(quality_scores)):
        assert quality_scores[i] >= quality_scores[i-1] - 0.05, \
            f"Quality should not significantly decrease: {quality_scores}"

def test_improvement_tracking():
    """Test that improvements are tracked correctly."""
    problem = "Build a recommendation system"

    output = run_agent_loop(problem, iterations=4)

    improvements = [s["improvement"] for s in output["solutions"]]

    # First improvement should be 0
    assert improvements[0] == 0.0, "First improvement should be 0"

    # Other improvements should be >= 0
    for imp in improvements[1:]:
        assert imp >= 0, f"Improvements should be non-negative: {improvements}"

def test_total_improvement_metric():
    """Test that total improvement is calculated correctly."""
    problem = "Optimize database query performance"

    output = run_agent_loop(problem, iterations=5)

    assert "total_improvement" in output, "Missing total_improvement"

    # Total improvement should be difference between last and first quality scores
    quality_scores = [s["quality_score"] for s in output["solutions"]]
    expected_improvement = round(quality_scores[-1] - quality_scores[0], 2)

    assert output["total_improvement"] == expected_improvement, \
        f"Total improvement mismatch: expected {expected_improvement}, got {output['total_improvement']}"

def test_convergence_rate():
    """Test that convergence rate is calculated."""
    problem = "Design a machine learning pipeline"

    output = run_agent_loop(problem, iterations=5)

    assert "convergence_rate" in output, "Missing convergence_rate"
    assert 0 <= output["convergence_rate"] <= 1, f"Convergence rate out of valid range: {output['convergence_rate']}"

def test_max_depth_tracking():
    """Test that maximum iteration depth is tracked."""
    problem = "Create a scalable microservices architecture"

    output = run_agent_loop(problem, iterations=5)

    assert "max_depth" in output, "Missing max_depth"
    assert output["max_depth"] == 5, f"Expected max_depth 5, got {output['max_depth']}"

def test_single_iteration():
    """Test with just one iteration."""
    problem = "Write a simple function"

    output = run_agent_loop(problem, iterations=1)

    assert len(output["solutions"]) == 1, "Should have 1 solution"
    assert output["solutions"][0]["improvement"] == 0.0, "First iteration should have 0 improvement"
    assert output["max_depth"] == 1, "Max depth should be 1"

def test_multiple_iterations():
    """Test with multiple iterations."""
    problem = "Solve the traveling salesman problem efficiently"

    output = run_agent_loop(problem, iterations=10)

    assert len(output["solutions"]) == 10, "Should have 10 solutions"
    assert output["max_depth"] == 10, "Max depth should be 10"
    assert output["iterations"] == 10, "Iterations count should be 10"

def test_empty_problem_error():
    """Test error handling for empty problem."""
    problem = ""
    output = run_agent_loop(problem, iterations=3)
    assert "error" in output, "Should error for empty problem"

def test_iteration_limits():
    """Test iteration count validation."""
    problem = "Simple problem"

    # Test valid limits
    output = run_agent_loop(problem, iterations=1)
    assert "solutions" in output, "Should handle iterations=1"

    output = run_agent_loop(problem, iterations=20)
    assert "solutions" in output, "Should handle iterations=20"

def test_solution_refinement_progression():
    """Test that solutions get longer/more detailed over iterations."""
    problem = "Implement a secure authentication system"

    output = run_agent_loop(problem, iterations=5)

    lengths = [s["length"] for s in output["solutions"]]

    # Solution lengths should generally increase as they're refined
    for i in range(1, len(lengths)):
        # Allow some variation but overall trend should be upward
        if i > 2:  # After a couple iterations
            assert lengths[i] >= lengths[0], \
                f"Later solutions should be more detailed: {lengths}"

def test_json_output_format():
    """Test that output is valid JSON with expected structure."""
    problem = "Build a real-time analytics platform"

    output = run_agent_loop(problem, iterations=3)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "problem" in output, "Missing problem"
    assert "iterations" in output, "Missing iterations"
    assert "total_improvement" in output, "Missing total_improvement"
    assert "convergence_rate" in output, "Missing convergence_rate"
    assert "max_depth" in output, "Missing max_depth"
    assert "execution_time_ms" in output, "Missing execution_time_ms"

    # Verify types
    assert isinstance(output["iterations"], int)
    assert isinstance(output["total_improvement"], (int, float))
    assert isinstance(output["convergence_rate"], (int, float))
    assert isinstance(output["max_depth"], int)
    assert isinstance(output["execution_time_ms"], (int, float))

def test_consistent_problem_reference():
    """Test that problem is consistently referenced."""
    problem = "Design a distributed file system"

    output = run_agent_loop(problem, iterations=4)

    # Problem should be in output (possibly truncated)
    assert "distributed" in output["problem"].lower() or "file" in output["problem"].lower(), \
        "Problem text should be present in output"

if __name__ == "__main__":
    test_basic_self_improvement()
    test_quality_progression()
    test_improvement_tracking()
    test_total_improvement_metric()
    test_convergence_rate()
    test_max_depth_tracking()
    test_single_iteration()
    test_multiple_iterations()
    test_empty_problem_error()
    test_iteration_limits()
    test_solution_refinement_progression()
    test_json_output_format()
    test_consistent_problem_reference()
    print("All tests passed!")
