from pathlib import Path
import subprocess
import json
import sys
import os

def run_fib(n):
    """Run the fib.py script and return parsed JSON output."""
    result = subprocess.run(
        [str(Path(__file__).parent.parent / 'solution.sh'), str(n)],
        capture_output=True,
        text=True,
        timeout=30
    )
    return json.loads(result.stdout)

def test_fibonacci_basic_cases():
    """Test basic Fibonacci values."""
    test_cases = [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (5, 5),
        (10, 55),
        (20, 6765),
    ]

    for n, expected in test_cases:
        output = run_fib(n)
        assert "memoized_result" in output, f"Missing memoized_result for n={n}"
        assert output["memoized_result"] == expected, \
            f"Memoized: Expected F({n}) = {expected}, got {output['memoized_result']}"

        # For small n, check recursive version too
        if n <= 25:
            assert "recursive_result" in output, f"Missing recursive_result for n={n}"
            assert output["recursive_result"] == expected, \
                f"Recursive: Expected F({n}) = {expected}, got {output['recursive_result']}"

def test_fibonacci_performance():
    """Test that memoized version is faster than recursive for n > 10."""
    output = run_fib(20)

    assert "recursive_time" in output, "Missing recursive_time"
    assert "memoized_time" in output, "Missing memoized_time"

    if output["recursive_time"] is not None and output["memoized_time"] is not None:
        assert output["memoized_time"] < output["recursive_time"], \
            f"Memoized ({output['memoized_time']}ms) should be faster than recursive ({output['recursive_time']}ms)"

def test_fibonacci_large_n():
    """Test Fibonacci with large n (using memoized version)."""
    output = run_fib(30)

    assert "memoized_result" in output, "Missing memoized_result for n=30"
    assert output["memoized_result"] == 832040, \
        f"Expected F(30) = 832040, got {output['memoized_result']}"
    assert "memoized_time" in output, "Missing memoized_time"
    assert output["memoized_time"] is not None, "memoized_time should not be None"

def test_fibonacci_edge_cases():
    """Test edge cases."""
    # Negative number
    output = run_fib(-1)
    assert "error" in output, "Should error for negative n"

    # Invalid input
    result = subprocess.run(
        [str(Path(__file__).parent.parent / 'solution.sh'), 'abc'],
        capture_output=True,
        text=True,
        timeout=30
    )
    output = json.loads(result.stdout)
    assert "error" in output, "Should error for non-integer input"

def test_fibonacci_json_format():
    """Test that output is valid JSON with expected fields."""
    output = run_fib(10)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "memoized_result" in output, "Missing memoized_result"
    assert "memoized_time" in output, "Missing memoized_time"
    assert isinstance(output["memoized_time"], (int, float)), "memoized_time should be numeric"

if __name__ == "__main__":
    test_fibonacci_basic_cases()
    test_fibonacci_performance()
    test_fibonacci_large_n()
    test_fibonacci_edge_cases()
    test_fibonacci_json_format()
    print("All tests passed!")
