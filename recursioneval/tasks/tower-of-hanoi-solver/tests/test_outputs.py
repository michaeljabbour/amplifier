from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile

def run_hanoi(config):
    """Run the hanoi solver and return parsed JSON output."""
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

def test_hanoi_3_disks():
    """Test Tower of Hanoi with 3 disks."""
    config = {"disks": 3, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    assert "moves" in output, "Missing 'moves' key"
    assert "total_moves" in output, "Missing 'total_moves' key"
    assert "recursion_depth" in output, "Missing 'recursion_depth' key"

    # For 3 disks, we need exactly 2^3 - 1 = 7 moves
    assert output["total_moves"] == 7, f"Expected 7 moves for 3 disks, got {output['total_moves']}"
    assert len(output["moves"]) == 7, f"Expected 7 moves in list, got {len(output['moves'])}"

    # Check move format
    for move in output["moves"]:
        assert isinstance(move, str), f"Move should be string, got {type(move)}"
        assert "->" in move, f"Move should contain '->', got {move}"
        parts = move.split("->")
        assert len(parts) == 2, f"Move format invalid: {move}"
        assert parts[0] in ["A", "B", "C"], f"Invalid source peg: {parts[0]}"
        assert parts[1] in ["A", "B", "C"], f"Invalid destination peg: {parts[1]}"

def test_hanoi_4_disks():
    """Test Tower of Hanoi with 4 disks."""
    config = {"disks": 4, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    # For 4 disks, we need exactly 2^4 - 1 = 15 moves
    assert output["total_moves"] == 15, f"Expected 15 moves for 4 disks, got {output['total_moves']}"

def test_hanoi_5_disks():
    """Test Tower of Hanoi with 5 disks."""
    config = {"disks": 5, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    # For 5 disks, we need exactly 2^5 - 1 = 31 moves
    assert output["total_moves"] == 31, f"Expected 31 moves for 5 disks, got {output['total_moves']}"

def test_hanoi_1_disk():
    """Test Tower of Hanoi with 1 disk (base case)."""
    config = {"disks": 1, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    # For 1 disk, we need exactly 1 move
    assert output["total_moves"] == 1, f"Expected 1 move for 1 disk, got {output['total_moves']}"
    assert output["moves"][0] == "A->C", f"Expected A->C, got {output['moves'][0]}"

def test_hanoi_recursion_depth():
    """Test that recursion depth is tracked."""
    config = {"disks": 3, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    assert "recursion_depth" in output, "Missing recursion_depth"
    assert output["recursion_depth"] > 0, "Recursion depth should be positive"
    # For n disks, max depth should be n
    assert output["recursion_depth"] <= config["disks"], \
        f"Recursion depth {output['recursion_depth']} should not exceed {config['disks']}"

def test_hanoi_custom_pegs():
    """Test Tower of Hanoi with custom peg names."""
    config = {"disks": 3, "source": "X", "destination": "Z", "auxiliary": "Y"}
    output = run_hanoi(config)

    assert output["total_moves"] == 7, f"Expected 7 moves, got {output['total_moves']}"
    # Verify all moves use the custom peg names
    for move in output["moves"]:
        parts = move.split("->")
        assert parts[0] in ["X", "Y", "Z"], f"Invalid peg in move: {move}"
        assert parts[1] in ["X", "Y", "Z"], f"Invalid peg in move: {move}"

def test_hanoi_execution_time():
    """Test that execution time is recorded."""
    config = {"disks": 3, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    assert "execution_time_ms" in output, "Missing execution_time_ms"
    assert isinstance(output["execution_time_ms"], (int, float)), \
        f"execution_time_ms should be numeric, got {type(output['execution_time_ms'])}"
    assert output["execution_time_ms"] >= 0, "execution_time_ms should be non-negative"

def test_hanoi_json_format():
    """Test that output is valid JSON with expected fields."""
    config = {"disks": 3, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert isinstance(output["moves"], list), "moves should be a list"
    assert isinstance(output["total_moves"], int), "total_moves should be an integer"
    assert isinstance(output["recursion_depth"], int), "recursion_depth should be an integer"

def test_hanoi_invalid_config():
    """Test error handling for invalid configs."""
    # Missing disks key
    config = {"source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)
    assert "error" in output, "Should error for missing disks"

    # Invalid disks value
    config = {"disks": "invalid", "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)
    assert "error" in output, "Should error for invalid disks"

    # Disks out of range
    config = {"disks": 0, "source": "A", "destination": "C", "auxiliary": "B"}
    output = run_hanoi(config)
    assert "error" in output, "Should error for disks < 1"

def test_hanoi_same_pegs():
    """Test error handling when source and destination are the same."""
    config = {"disks": 3, "source": "A", "destination": "A", "auxiliary": "B"}
    output = run_hanoi(config)
    assert "error" in output, "Should error when source == destination"

if __name__ == "__main__":
    test_hanoi_3_disks()
    test_hanoi_4_disks()
    test_hanoi_5_disks()
    test_hanoi_1_disk()
    test_hanoi_recursion_depth()
    test_hanoi_custom_pegs()
    test_hanoi_execution_time()
    test_hanoi_json_format()
    test_hanoi_invalid_config()
    test_hanoi_same_pegs()
    print("All tests passed!")
