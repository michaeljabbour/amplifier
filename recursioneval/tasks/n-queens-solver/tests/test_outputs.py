from pathlib import Path
import subprocess
import json
import sys
import tempfile
import os

def run_nqueens(n):
    """Run the nqueens.py script and return parsed JSON output."""
    config = {"n": n}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_file = f.name

    try:
        result = subprocess.run(
            [str(Path(__file__).parent.parent / 'solution.sh'), config_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        return json.loads(result.stdout)
    finally:
        os.unlink(config_file)

def is_valid_solution(placement, n):
    """Verify a queen placement is valid (no attacking queens)."""
    # Check all pairs of queens
    for row1 in range(n):
        for row2 in range(row1 + 1, n):
            col1 = placement[row1]
            col2 = placement[row2]

            # Same column
            if col1 == col2:
                return False

            # Same diagonal
            if abs(col1 - col2) == abs(row1 - row2):
                return False

    return True

def test_n_equals_1():
    """Test N=1 (trivial case)."""
    output = run_nqueens(1)

    assert "solutions_count" in output, "Missing solutions_count"
    assert output["solutions_count"] == 1, f"Expected 1 solution for N=1, got {output['solutions_count']}"
    assert output["n"] == 1, "Output n mismatch"

def test_n_equals_4():
    """Test N=4 (2 solutions exist)."""
    output = run_nqueens(4)

    assert output["n"] == 4, "Output n mismatch"
    assert output["solutions_count"] == 2, \
        f"Expected 2 solutions for N=4, got {output['solutions_count']}"

    # Verify each solution is valid
    for solution in output["solutions"]:
        placement = solution["placement"]
        assert len(placement) == 4, f"Placement should have length 4, got {len(placement)}"
        assert is_valid_solution(placement, 4), \
            f"Invalid solution found: {placement}"

    assert "max_recursion_depth" in output, "Missing max_recursion_depth"
    assert output["max_recursion_depth"] > 0, "max_recursion_depth should be positive"

def test_n_equals_8():
    """Test N=8 (92 solutions exist - verify at least one found)."""
    output = run_nqueens(8)

    assert output["n"] == 8, "Output n mismatch"
    assert output["solutions_count"] > 0, "Should find at least one solution for N=8"
    assert output["solutions_count"] == 92, \
        f"Expected 92 solutions for N=8, got {output['solutions_count']}"

    # Verify each solution is valid
    for solution in output["solutions"]:
        placement = solution["placement"]
        assert len(placement) == 8, f"Placement should have length 8, got {len(placement)}"
        assert is_valid_solution(placement, 8), \
            f"Invalid solution found: {placement}"

def test_solution_structure():
    """Test the structure of the output JSON."""
    output = run_nqueens(4)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "n" in output, "Missing 'n' field"
    assert "solutions_count" in output, "Missing 'solutions_count' field"
    assert "solutions" in output, "Missing 'solutions' field"
    assert "max_recursion_depth" in output, "Missing 'max_recursion_depth' field"
    assert "execution_time_ms" in output, "Missing 'execution_time_ms' field"

    assert isinstance(output["solutions"], list), "solutions should be a list"
    assert isinstance(output["max_recursion_depth"], int), "max_recursion_depth should be int"
    assert isinstance(output["execution_time_ms"], (int, float)), "execution_time_ms should be numeric"

def test_board_visualization():
    """Test that board visualization matches placement."""
    output = run_nqueens(4)

    for solution in output["solutions"]:
        placement = solution["placement"]
        board = solution["board"]

        assert len(board) == 4, "Board should have 4 rows"
        for row_idx, col_idx in enumerate(placement):
            assert board[row_idx][col_idx] == 1, \
                f"Queen should be at board[{row_idx}][{col_idx}]"
            # All other cells in the row should be 0
            for col in range(4):
                if col != col_idx:
                    assert board[row_idx][col] == 0, \
                        f"Should not have queen at board[{row_idx}][{col}]"

def test_n_equals_2_and_3():
    """Test N=2 and N=3 (no solutions exist)."""
    for n in [2, 3]:
        output = run_nqueens(n)
        assert output["n"] == n, f"Output n mismatch for N={n}"
        assert output["solutions_count"] == 0, \
            f"Expected 0 solutions for N={n}, got {output['solutions_count']}"

def test_recursion_depth_tracking():
    """Test that recursion depth is tracked correctly."""
    output = run_nqueens(5)

    max_depth = output["max_recursion_depth"]
    assert max_depth > 0, "max_recursion_depth should be positive"
    # For N=5, depth should be at most 5 (one level per row) plus some backtracking depth
    assert max_depth <= 10, f"max_recursion_depth seems too high: {max_depth}"

def test_placement_values():
    """Test that placements contain valid column indices."""
    output = run_nqueens(6)

    for solution in output["solutions"]:
        placement = solution["placement"]
        for col_idx in placement:
            assert 0 <= col_idx < 6, \
                f"Column index {col_idx} out of range [0, 5]"

if __name__ == "__main__":
    test_n_equals_1()
    test_n_equals_2_and_3()
    test_n_equals_4()
    test_solution_structure()
    test_board_visualization()
    test_placement_values()
    test_recursion_depth_tracking()
    test_n_equals_8()
    print("All tests passed!")
