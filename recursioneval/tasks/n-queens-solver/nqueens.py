import sys
import json
import time

class NQueensSolver:
    def __init__(self, n):
        self.n = n
        self.solutions = []
        self.max_depth = 0
        self.current_depth = 0

    def is_safe(self, board, row, col):
        """Check if placing a queen at (row, col) is safe."""
        # Check column
        for i in range(row):
            if board[i] == col:
                return False

        # Check upper left diagonal
        for i in range(row):
            if abs(board[i] - col) == abs(i - row):
                return False

        return True

    def solve(self, board, row):
        """Recursively solve N-Queens using backtracking."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        # Base case: all queens placed
        if row == self.n:
            self.solutions.append(board[:])
            self.current_depth -= 1
            return

        # Try placing queen in each column of current row
        for col in range(self.n):
            if self.is_safe(board, row, col):
                board[row] = col
                self.solve(board, row + 1)
                board[row] = -1  # Backtrack

        self.current_depth -= 1

    def get_board_visualization(self, placement):
        """Convert placement array to board visualization."""
        board = []
        for row in range(self.n):
            board_row = [0] * self.n
            board_row[placement[row]] = 1
            board.append(board_row)
        return board

    def solve_all(self):
        """Find all solutions."""
        board = [-1] * self.n
        self.current_depth = 0
        self.max_depth = 0
        self.solve(board, 0)
        return self.solutions

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python nqueens.py <config_file>"}))
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Failed to read config: {str(e)}"}))
        sys.exit(1)

    if "n" not in config:
        print(json.dumps({"error": "Missing 'n' key in config"}))
        sys.exit(1)

    try:
        n = int(config["n"])
    except (ValueError, TypeError):
        print(json.dumps({"error": f"Invalid n: {config['n']}"}))
        sys.exit(1)

    if n < 1 or n > 15:
        print(json.dumps({"error": f"n must be between 1 and 15, got {n}"}))
        sys.exit(1)

    start_time = time.time()

    solver = NQueensSolver(n)
    solutions = solver.solve_all()

    elapsed_ms = (time.time() - start_time) * 1000

    # Format output
    results = {
        "n": n,
        "solutions_count": len(solutions),
        "solutions": [],
        "max_recursion_depth": solver.max_depth,
        "execution_time_ms": round(elapsed_ms, 2)
    }

    # Add solutions with board visualizations
    for placement in solutions:
        results["solutions"].append({
            "placement": placement,
            "board": solver.get_board_visualization(placement)
        })

    print(json.dumps(results))

if __name__ == "__main__":
    main()
