#!/bin/bash
set -e

# Write the recursive planner script
cat > planner.py << 'EOF'
import sys
import json
import time
import uuid

class RecursivePlanner:
    def __init__(self):
        self.execution_plan = []
        self.max_depth = 0
        self.current_depth = 0
        self.task_counter = 0

    def decompose(self, task_spec, parent_depth=0):
        """Recursively decompose a task."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        task_name = task_spec.get("task", "Unknown Task")
        is_decomposable = task_spec.get("decomposable", False)
        subtasks = task_spec.get("subtasks", [])

        # Generate task ID
        self.task_counter += 1
        task_id = str(self.task_counter)

        if not is_decomposable or not subtasks:
            # Leaf task: add to execution plan
            plan_entry = {
                "id": task_id,
                "task": task_name,
                "subtasks": [],
                "depth": parent_depth + 1,
                "decomposition_level": self.current_depth
            }
            self.execution_plan.append(plan_entry)
            self.current_depth -= 1
            return [plan_entry]

        else:
            # Decomposable task: process subtasks recursively
            subtask_ids = []
            for subtask in subtasks:
                results = self.decompose(subtask, parent_depth + 1)
                subtask_ids.extend([r["id"] for r in results])

            # Add parent task to plan
            plan_entry = {
                "id": task_id,
                "task": task_name,
                "subtasks": subtask_ids,
                "depth": parent_depth + 1,
                "decomposition_level": self.current_depth
            }
            self.execution_plan.append(plan_entry)
            self.current_depth -= 1
            return [plan_entry]

    def plan(self, root_task):
        """Generate execution plan for a root task."""
        self.current_depth = 0
        self.max_depth = 0
        self.task_counter = 0
        self.execution_plan = []

        self.decompose(root_task, parent_depth=0)

        return self.execution_plan

def validate_task_spec(task_spec):
    """Validate the task specification structure."""
    if not isinstance(task_spec, dict):
        raise ValueError("Task spec must be a dictionary")

    if "task" not in task_spec:
        raise ValueError("Task spec must have a 'task' field")

    task_name = task_spec.get("task")
    if not isinstance(task_name, str):
        raise ValueError(f"Task name must be a string, got {type(task_name).__name__}")

    decomposable = task_spec.get("decomposable", False)
    if not isinstance(decomposable, bool):
        raise ValueError(f"decomposable must be boolean, got {type(decomposable).__name__}")

    if decomposable:
        subtasks = task_spec.get("subtasks", [])
        if not isinstance(subtasks, list):
            raise ValueError(f"subtasks must be a list, got {type(subtasks).__name__}")

        for i, subtask in enumerate(subtasks):
            try:
                validate_task_spec(subtask)
            except ValueError as e:
                raise ValueError(f"Invalid subtask at index {i}: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python planner.py <config_file>"}))
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Failed to read config: {str(e)}"}))
        sys.exit(1)

    if "task" not in config:
        print(json.dumps({"error": "Missing 'task' field in config"}))
        sys.exit(1)

    try:
        validate_task_spec(config)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    start_time = time.time()

    try:
        planner = RecursivePlanner()
        execution_plan = planner.plan(config)

        elapsed_ms = (time.time() - start_time) * 1000

        # Calculate task hierarchy depth (max depth in the tree)
        max_tree_depth = max((entry["depth"] for entry in execution_plan), default=0)

        # Format output
        output = {
            "original_task": config.get("task", ""),
            "execution_plan": execution_plan,
            "total_tasks": len(execution_plan),
            "max_depth": max_tree_depth,
            "recursion_depth": planner.max_depth,
            "execution_time_ms": round(elapsed_ms, 2)
        }

        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

python3 planner.py "$@"
