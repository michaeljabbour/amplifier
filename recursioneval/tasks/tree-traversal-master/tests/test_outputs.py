from pathlib import Path
import subprocess
import json
import sys
import tempfile
import os

def run_traverse(config_dict):
    """Run the traverse.py script and return parsed JSON output."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_dict, f)
        config_file = f.name

    try:
        result = subprocess.run(
            [str(Path(__file__).parent.parent / 'solution.sh'), config_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        return json.loads(result.stdout)
    finally:
        os.unlink(config_file)

def test_simple_tree():
    """Test a simple binary tree."""
    config = {"tree": [1, 2, 3]}
    output = run_traverse(config)

    assert "inorder" in output, "Missing inorder"
    assert "preorder" in output, "Missing preorder"
    assert "postorder" in output, "Missing postorder"
    assert "recursion_depth" in output, "Missing recursion_depth"

    # For tree [1, 2, 3]:
    #      1
    #     / \
    #    2   3
    assert output["inorder"] == [2, 1, 3], f"Expected [2, 1, 3], got {output['inorder']}"
    assert output["preorder"] == [1, 2, 3], f"Expected [1, 2, 3], got {output['preorder']}"
    assert output["postorder"] == [2, 3, 1], f"Expected [2, 3, 1], got {output['postorder']}"

def test_larger_tree():
    """Test a larger binary tree with null nodes."""
    # Tree: [1, 2, 3, 4, 5, null, 6]
    #        1
    #       / \
    #      2   3
    #     / \ 　\
    #    4  5    6
    config = {"tree": [1, 2, 3, 4, 5, None, 6]}
    output = run_traverse(config)

    assert output["inorder"] == [4, 2, 5, 1, 3, 6], f"Got {output['inorder']}"
    assert output["preorder"] == [1, 2, 4, 5, 3, 6], f"Got {output['preorder']}"
    assert output["postorder"] == [4, 5, 2, 6, 3, 1], f"Got {output['postorder']}"

def test_single_node():
    """Test a tree with a single node."""
    config = {"tree": [42]}
    output = run_traverse(config)

    assert output["inorder"] == [42], f"Expected [42], got {output['inorder']}"
    assert output["preorder"] == [42], f"Expected [42], got {output['preorder']}"
    assert output["postorder"] == [42], f"Expected [42], got {output['postorder']}"
    assert output["recursion_depth"] == 1, f"Expected depth 1, got {output['recursion_depth']}"

def test_empty_tree():
    """Test an empty tree."""
    config = {"tree": []}
    output = run_traverse(config)

    assert output["inorder"] == [], f"Expected [], got {output['inorder']}"
    assert output["preorder"] == [], f"Expected [], got {output['preorder']}"
    assert output["postorder"] == [], f"Expected [], got {output['postorder']}"
    assert output["recursion_depth"] == 0, f"Expected depth 0, got {output['recursion_depth']}"

def test_null_root():
    """Test tree with null root."""
    config = {"tree": [None]}
    output = run_traverse(config)

    assert output["inorder"] == [], f"Expected [], got {output['inorder']}"
    assert output["preorder"] == [], f"Expected [], got {output['preorder']}"
    assert output["postorder"] == [], f"Expected [], got {output['postorder']}"

def test_unbalanced_tree():
    """Test a completely unbalanced tree (linked list-like)."""
    # Tree: [1, 2, null, 3, null, null, null]
    #    1
    #   /
    #  2
    # /
    #3
    config = {"tree": [1, 2, None, 3]}
    output = run_traverse(config)

    assert output["inorder"] == [3, 2, 1], f"Got {output['inorder']}"
    assert output["preorder"] == [1, 2, 3], f"Got {output['preorder']}"
    assert output["postorder"] == [3, 2, 1], f"Got {output['postorder']}"
    assert output["recursion_depth"] >= 3, f"Expected depth >= 3, got {output['recursion_depth']}"

def test_traversal_counts():
    """Test that all traversals visit the same number of nodes."""
    config = {"tree": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    output = run_traverse(config)

    inorder_count = len(output["inorder"])
    preorder_count = len(output["preorder"])
    postorder_count = len(output["postorder"])
    total_nodes = 10

    assert inorder_count == total_nodes, \
        f"Inorder visited {inorder_count} nodes, expected {total_nodes}"
    assert preorder_count == total_nodes, \
        f"Preorder visited {preorder_count} nodes, expected {total_nodes}"
    assert postorder_count == total_nodes, \
        f"Postorder visited {postorder_count} nodes, expected {total_nodes}"

def test_json_format():
    """Test that output is valid JSON with expected structure."""
    config = {"tree": [1, 2, 3]}
    output = run_traverse(config)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert isinstance(output["inorder"], list), "inorder should be a list"
    assert isinstance(output["preorder"], list), "preorder should be a list"
    assert isinstance(output["postorder"], list), "postorder should be a list"
    assert isinstance(output["recursion_depth"], int), "recursion_depth should be an integer"

if __name__ == "__main__":
    test_simple_tree()
    test_larger_tree()
    test_single_node()
    test_empty_tree()
    test_null_root()
    test_unbalanced_tree()
    test_traversal_counts()
    test_json_format()
    print("All tests passed!")
