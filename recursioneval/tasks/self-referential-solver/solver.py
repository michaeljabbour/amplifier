import sys
import json
import time
from collections import defaultdict, deque

class SelfReferentialSolver:
    def __init__(self):
        self.solutions = {}
        self.call_chain = []
        self.max_depth = 0
        self.step_counter = 0

    def topological_sort(self, subproblems):
        """Sort subproblems by dependencies using topological sort."""
        # Build adjacency list
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        problem_map = {sp["id"]: sp for sp in subproblems}

        for problem in subproblems:
            prob_id = problem["id"]
            if prob_id not in in_degree:
                in_degree[prob_id] = 0
            dependencies = problem.get("depends_on", [])
            for dep in dependencies:
                graph[dep].append(prob_id)
                in_degree[prob_id] += 1

        # Kahn's algorithm
        queue = deque([pid for pid in problem_map.keys() if in_degree[pid] == 0])
        sorted_order = []

        while queue:
            current = queue.popleft()
            sorted_order.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_order) != len(problem_map):
            raise ValueError("Circular dependency detected in subproblems")

        return sorted_order

    def generate_solution(self, subproblem, previous_solutions, depth):
        """Generate a solution for a subproblem referencing previous solutions."""
        description = subproblem.get("description", "")
        dependencies = subproblem.get("depends_on", [])

        # Build reference string from previous solutions
        reference_str = ""
        if dependencies:
            reference_str = " Based on: "
            refs = []
            for dep_id in dependencies:
                if dep_id in previous_solutions:
                    refs.append(f"Step {dep_id} ({previous_solutions[dep_id]['summary']})")
            reference_str += "; ".join(refs) + "."

        # Simple solution generation based on problem description
        solution = f"Solve: {description}{reference_str}"

        return solution

    def solve(self, problem_spec):
        """Solve the problem using self-referential decomposition."""
        problem_text = problem_spec.get("problem", "")
        subproblems = problem_spec.get("subproblems", [])

        if not subproblems:
            raise ValueError("No subproblems defined")

        # Validate all subproblems have IDs
        for sp in subproblems:
            if "id" not in sp:
                raise ValueError("All subproblems must have an 'id' field")

        # Topologically sort subproblems by dependencies
        sorted_ids = self.topological_sort(subproblems)
        problem_map = {sp["id"]: sp for sp in subproblems}

        solution_chain = []
        dependency_count = 0

        for order_idx, prob_id in enumerate(sorted_ids):
            self.step_counter += 1
            depth = order_idx + 1
            self.max_depth = max(self.max_depth, depth)

            subproblem = problem_map[prob_id]
            dependencies = subproblem.get("depends_on", [])
            dependency_count += len(dependencies)

            # Generate solution referencing previous solutions
            solution = self.generate_solution(subproblem, self.solutions, depth)

            # Store solution for later reference
            summary = subproblem.get("description", "")[:30]
            self.solutions[prob_id] = {
                "solution": solution,
                "summary": summary
            }

            # Add to solution chain
            chain_entry = {
                "step": self.step_counter,
                "problem_id": prob_id,
                "subproblem": subproblem.get("description", ""),
                "solution": solution,
                "depth": depth,
                "dependencies": dependencies
            }
            solution_chain.append(chain_entry)

        return solution_chain, dependency_count

def validate_problem_spec(spec):
    """Validate problem specification structure."""
    if not isinstance(spec, dict):
        raise ValueError("Problem spec must be a dictionary")

    if "problem" not in spec:
        raise ValueError("Problem spec must have a 'problem' field")

    if "subproblems" not in spec:
        raise ValueError("Problem spec must have a 'subproblems' field")

    subproblems = spec["subproblems"]
    if not isinstance(subproblems, list):
        raise ValueError(f"subproblems must be a list, got {type(subproblems).__name__}")

    if not subproblems:
        raise ValueError("subproblems cannot be empty")

    for i, sp in enumerate(subproblems):
        if not isinstance(sp, dict):
            raise ValueError(f"Subproblem {i} must be a dict")
        if "id" not in sp:
            raise ValueError(f"Subproblem {i} must have an 'id' field")
        if "description" not in sp:
            raise ValueError(f"Subproblem {i} must have a 'description' field")

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python solver.py <problem_file>"}))
        sys.exit(1)

    problem_file = sys.argv[1]

    try:
        with open(problem_file, 'r') as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {problem_file}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    try:
        validate_problem_spec(spec)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    start_time = time.time()

    try:
        solver = SelfReferentialSolver()
        solution_chain, dependency_count = solver.solve(spec)

        elapsed_ms = (time.time() - start_time) * 1000

        output = {
            "problem": spec.get("problem", ""),
            "solution_chain": solution_chain,
            "total_steps": len(solution_chain),
            "max_depth": solver.max_depth,
            "dependency_count": dependency_count,
            "execution_time_ms": round(elapsed_ms, 2)
        }

        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
