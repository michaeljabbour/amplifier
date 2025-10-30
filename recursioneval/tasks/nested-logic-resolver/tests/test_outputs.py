from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile

def run_logic(config):
    """Run the logic resolver and return parsed JSON output."""
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

def test_logic_simple_and():
    """Test simple AND operation."""
    config = {
        "expression": "AND(A, B)",
        "values": {"A": True, "B": True}
    }
    output = run_logic(config)
    assert output["result"] == True, f"AND(True, True) should be True, got {output['result']}"

def test_logic_simple_or():
    """Test simple OR operation."""
    config = {
        "expression": "OR(A, B)",
        "values": {"A": False, "B": True}
    }
    output = run_logic(config)
    assert output["result"] == True, f"OR(False, True) should be True, got {output['result']}"

def test_logic_simple_not():
    """Test simple NOT operation."""
    config = {
        "expression": "NOT(A)",
        "values": {"A": True}
    }
    output = run_logic(config)
    assert output["result"] == False, f"NOT(True) should be False, got {output['result']}"

def test_logic_nested_and_or():
    """Test nested AND/OR operations."""
    config = {
        "expression": "AND(OR(A, B), C)",
        "values": {"A": False, "B": False, "C": True}
    }
    output = run_logic(config)
    assert output["result"] == False, f"AND(OR(False, False), True) should be False, got {output['result']}"

def test_logic_complex_nested():
    """Test complex nested expression."""
    config = {
        "expression": "OR(AND(A, B), NOT(C))",
        "values": {"A": True, "B": False, "C": True}
    }
    output = run_logic(config)
    # AND(A, B) = AND(True, False) = False
    # NOT(C) = NOT(True) = False
    # OR(False, False) = False
    assert output["result"] == False, f"Expected False, got {output['result']}"

def test_logic_if_then():
    """Test IF_THEN operation."""
    config = {
        "expression": "IF_THEN(A, B)",
        "values": {"A": True, "B": False}
    }
    output = run_logic(config)
    # IF_THEN(True, False) = False (only case where IF_THEN is false)
    assert output["result"] == False, f"IF_THEN(True, False) should be False, got {output['result']}"

def test_logic_if_then_true():
    """Test IF_THEN when both are true."""
    config = {
        "expression": "IF_THEN(A, B)",
        "values": {"A": True, "B": True}
    }
    output = run_logic(config)
    assert output["result"] == True, f"IF_THEN(True, True) should be True, got {output['result']}"

def test_logic_iff():
    """Test IFF (if and only if) operation."""
    config = {
        "expression": "IFF(A, B)",
        "values": {"A": True, "B": True}
    }
    output = run_logic(config)
    assert output["result"] == True, f"IFF(True, True) should be True, got {output['result']}"

def test_logic_iff_different():
    """Test IFF with different values."""
    config = {
        "expression": "IFF(A, B)",
        "values": {"A": True, "B": False}
    }
    output = run_logic(config)
    assert output["result"] == False, f"IFF(True, False) should be False, got {output['result']}"

def test_logic_deeply_nested():
    """Test deeply nested expression."""
    config = {
        "expression": "NOT(AND(OR(A, B), NOT(AND(C, D))))",
        "values": {"A": True, "B": False, "C": True, "D": True}
    }
    output = run_logic(config)

    assert "result" in output, "Missing 'result' key"
    assert isinstance(output["result"], bool), f"Result should be boolean, got {type(output['result'])}"

def test_logic_recursion_depth():
    """Test that recursion depth is tracked."""
    config = {
        "expression": "NOT(AND(OR(A, B), C))",
        "values": {"A": True, "B": False, "C": True}
    }
    output = run_logic(config)

    assert "recursion_depth" in output, "Missing recursion_depth"
    assert output["recursion_depth"] > 0, "Recursion depth should be positive"

def test_logic_evaluation_steps():
    """Test that evaluation steps are recorded."""
    config = {
        "expression": "AND(A, B)",
        "values": {"A": True, "B": False}
    }
    output = run_logic(config)

    assert "evaluation_steps" in output, "Missing evaluation_steps"
    assert isinstance(output["evaluation_steps"], list), "evaluation_steps should be a list"
    assert len(output["evaluation_steps"]) > 0, "evaluation_steps should not be empty"

    # Each step should have expression, result, and depth
    for step in output["evaluation_steps"]:
        assert "expression" in step, "Step missing expression"
        assert "result" in step, "Step missing result"
        assert "depth" in step, "Step missing depth"
        assert isinstance(step["result"], bool), f"Step result should be boolean, got {type(step['result'])}"

def test_logic_execution_time():
    """Test that execution time is recorded."""
    config = {
        "expression": "AND(A, B)",
        "values": {"A": True, "B": False}
    }
    output = run_logic(config)

    assert "execution_time_ms" in output, "Missing execution_time_ms"
    assert isinstance(output["execution_time_ms"], (int, float)), \
        f"execution_time_ms should be numeric, got {type(output['execution_time_ms'])}"
    assert output["execution_time_ms"] >= 0, "execution_time_ms should be non-negative"

def test_logic_json_format():
    """Test that output is valid JSON with expected fields."""
    config = {
        "expression": "A",
        "values": {"A": True}
    }
    output = run_logic(config)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "expression" in output, "Missing expression"
    assert "result" in output, "Missing result"
    assert "recursion_depth" in output, "Missing recursion_depth"
    assert "evaluation_steps" in output, "Missing evaluation_steps"
    assert "execution_time_ms" in output, "Missing execution_time_ms"

def test_logic_invalid_config():
    """Test error handling for invalid configs."""
    # Missing expression
    config = {"values": {"A": True}}
    output = run_logic(config)
    assert "error" in output, "Should error for missing expression"

    # Missing values
    config = {"expression": "A"}
    output = run_logic(config)
    assert "error" in output, "Should error for missing values"

    # Invalid value type
    config = {"expression": "A", "values": {"A": "true"}}
    output = run_logic(config)
    assert "error" in output, "Should error for non-boolean value"

def test_logic_undefined_variable():
    """Test error handling for undefined variables."""
    config = {
        "expression": "A",
        "values": {"B": True}
    }
    output = run_logic(config)
    assert "error" in output, "Should error for undefined variable"

def test_logic_multiple_variables():
    """Test expression with multiple variables."""
    config = {
        "expression": "AND(A, OR(B, C), NOT(D))",
        "values": {"A": True, "B": False, "C": True, "D": False}
    }
    output = run_logic(config)

    # AND(A, OR(B, C), NOT(D)) = AND(True, OR(False, True), NOT(False)) = AND(True, True, True) = True
    assert output["result"] == True, f"Expected True, got {output['result']}"

if __name__ == "__main__":
    test_logic_simple_and()
    test_logic_simple_or()
    test_logic_simple_not()
    test_logic_nested_and_or()
    test_logic_complex_nested()
    test_logic_if_then()
    test_logic_if_then_true()
    test_logic_iff()
    test_logic_iff_different()
    test_logic_deeply_nested()
    test_logic_recursion_depth()
    test_logic_evaluation_steps()
    test_logic_execution_time()
    test_logic_json_format()
    test_logic_invalid_config()
    test_logic_undefined_variable()
    test_logic_multiple_variables()
    print("All tests passed!")
