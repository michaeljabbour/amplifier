#!/bin/bash
set -e

# Write the tree traversal script
cat > traverse.py << 'EOF'
import sys
import json

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class TreeTraversal:
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def build_tree(self, arr):
        """Build binary tree from level-order array representation."""
        if not arr or arr[0] is None:
            return None

        root = TreeNode(arr[0])
        queue = [(root, 0)]
        idx = 1

        while queue and idx < len(arr):
            node, level = queue.pop(0)

            # Left child
            left_idx = 2 * level + 1
            if left_idx < len(arr) and arr[left_idx] is not None:
                node.left = TreeNode(arr[left_idx])
                queue.append((node.left, left_idx))

            # Right child
            right_idx = 2 * level + 2
            if right_idx < len(arr) and arr[right_idx] is not None:
                node.right = TreeNode(arr[right_idx])
                queue.append((node.right, right_idx))

        return root

    def inorder(self, node, result=None):
        """Traverse: Left -> Node -> Right"""
        if result is None:
            result = []
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        if node is None:
            self.current_depth -= 1
            return result

        self.inorder(node.left, result)
        result.append(node.val)
        self.inorder(node.right, result)

        self.current_depth -= 1
        return result

    def preorder(self, node, result=None):
        """Traverse: Node -> Left -> Right"""
        if result is None:
            result = []
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        if node is None:
            self.current_depth -= 1
            return result

        result.append(node.val)
        self.preorder(node.left, result)
        self.preorder(node.right, result)

        self.current_depth -= 1
        return result

    def postorder(self, node, result=None):
        """Traverse: Left -> Right -> Node"""
        if result is None:
            result = []
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        if node is None:
            self.current_depth -= 1
            return result

        self.postorder(node.left, result)
        self.postorder(node.right, result)
        result.append(node.val)

        self.current_depth -= 1
        return result

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python traverse.py <config_file>"}))
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Failed to read config: {str(e)}"}))
        sys.exit(1)

    if "tree" not in config:
        print(json.dumps({"error": "Missing 'tree' key in config"}))
        sys.exit(1)

    tree_array = config["tree"]

    traversal = TreeTraversal()
    root = traversal.build_tree(tree_array)

    # Reset depth tracking for each traversal
    results = {}

    if root:
        traversal.max_depth = 0
        traversal.current_depth = 0
        results["inorder"] = traversal.inorder(root)

        traversal.max_depth = 0
        traversal.current_depth = 0
        results["preorder"] = traversal.preorder(root)

        traversal.max_depth = 0
        traversal.current_depth = 0
        results["postorder"] = traversal.postorder(root)

        results["recursion_depth"] = traversal.max_depth
    else:
        results["inorder"] = []
        results["preorder"] = []
        results["postorder"] = []
        results["recursion_depth"] = 0

    print(json.dumps(results))

if __name__ == "__main__":
    main()
EOF

python3 traverse.py "$@"
