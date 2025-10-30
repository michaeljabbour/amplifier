import sys
import json
import time

class HanoiSolver:
    def __init__(self, disks, source, destination, auxiliary):
        self.disks = disks
        self.source = source
        self.destination = destination
        self.auxiliary = auxiliary
        self.moves = []
        self.max_depth = 0
        self.current_depth = 0
        # Track pegs state for validation
        self.pegs = {source: list(range(disks, 0, -1)), destination: [], auxiliary: []}

    def is_valid_move(self, from_peg, to_peg):
        """Verify that a move follows the Tower of Hanoi rules."""
        if not self.pegs[from_peg]:
            return False
        if self.pegs[to_peg] and self.pegs[from_peg][-1] > self.pegs[to_peg][-1]:
            return False
        return True

    def make_move(self, from_peg, to_peg):
        """Execute a move and record it."""
        if not self.is_valid_move(from_peg, to_peg):
            raise ValueError(f"Invalid move: {from_peg} -> {to_peg}")
        disk = self.pegs[from_peg].pop()
        self.pegs[to_peg].append(disk)
        self.moves.append(f"{from_peg}->{to_peg}")

    def solve(self, n, source, destination, auxiliary):
        """Recursively solve Tower of Hanoi."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        if n == 1:
            self.make_move(source, destination)
            self.current_depth -= 1
            return

        # Move n-1 disks from source to auxiliary using destination
        self.solve(n - 1, source, auxiliary, destination)
        # Move the largest disk from source to destination
        self.make_move(source, destination)
        # Move n-1 disks from auxiliary to destination using source
        self.solve(n - 1, auxiliary, destination, source)

        self.current_depth -= 1

    def solve_all(self):
        """Find the optimal move sequence."""
        self.current_depth = 0
        self.max_depth = 0
        self.solve(self.disks, self.source, self.destination, self.auxiliary)
        return self.moves

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python hanoi.py <config_file>"}))
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Failed to read config: {str(e)}"}))
        sys.exit(1)

    # Validate config
    required_keys = {"disks", "source", "destination", "auxiliary"}
    if not required_keys.issubset(config.keys()):
        print(json.dumps({"error": f"Missing required keys: {required_keys - set(config.keys())}"}))
        sys.exit(1)

    try:
        disks = int(config["disks"])
    except (ValueError, TypeError):
        print(json.dumps({"error": f"Invalid disks: {config['disks']}"}))
        sys.exit(1)

    if disks < 1 or disks > 20:
        print(json.dumps({"error": f"disks must be between 1 and 20, got {disks}"}))
        sys.exit(1)

    source = config.get("source", "A")
    destination = config.get("destination", "C")
    auxiliary = config.get("auxiliary", "B")

    # Validate pegs are different
    pegs = {source, destination, auxiliary}
    if len(pegs) != 3:
        print(json.dumps({"error": "source, destination, and auxiliary must be different"}))
        sys.exit(1)

    start_time = time.time()

    solver = HanoiSolver(disks, source, destination, auxiliary)
    moves = solver.solve_all()

    elapsed_ms = (time.time() - start_time) * 1000

    # Verify the solution
    expected_moves = (2 ** disks) - 1
    if len(moves) != expected_moves:
        print(json.dumps({
            "error": f"Invalid solution: got {len(moves)} moves but expected {expected_moves}"
        }))
        sys.exit(1)

    # Verify final state
    if len(solver.pegs[destination]) != disks:
        print(json.dumps({
            "error": "Invalid solution: not all disks are on the destination peg"
        }))
        sys.exit(1)

    # Format output
    results = {
        "moves": moves,
        "total_moves": len(moves),
        "recursion_depth": solver.max_depth,
        "execution_time_ms": round(elapsed_ms, 2)
    }

    print(json.dumps(results))

if __name__ == "__main__":
    main()
