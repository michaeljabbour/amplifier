#!/bin/bash
set -e

# Write the Fibonacci calculator script
cat > fib.py << 'EOF'
import sys
import json
import time

def fib_recursive(n):
    """Compute Fibonacci number using pure recursion."""
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

def fib_memoized(n, memo=None):
    """Compute Fibonacci number using memoization."""
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memoized(n - 1, memo) + fib_memoized(n - 2, memo)
    return memo[n]

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python fib.py <n>"}))
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print(json.dumps({"error": f"Invalid input: {sys.argv[1]} is not an integer"}))
        sys.exit(1)

    if n < 0:
        print(json.dumps({"error": f"Invalid input: n must be non-negative, got {n}"}))
        sys.exit(1)

    # For large n with pure recursion, we limit to avoid timeout
    if n > 30:
        print(json.dumps({"error": f"n too large: {n} (max 30)"}))
        sys.exit(1)

    results = {}

    # Recursive version (only for n <= 25 to avoid timeout)
    if n <= 25:
        start = time.time()
        recursive_result = fib_recursive(n)
        recursive_time = (time.time() - start) * 1000  # Convert to ms
        results["recursive_result"] = recursive_result
        results["recursive_time"] = round(recursive_time, 2)
    else:
        results["recursive_result"] = None
        results["recursive_time"] = None

    # Memoized version (fast even for large n)
    start = time.time()
    memoized_result = fib_memoized(n)
    memoized_time = (time.time() - start) * 1000  # Convert to ms
    results["memoized_result"] = memoized_result
    results["memoized_time"] = round(memoized_time, 2)

    print(json.dumps(results))

if __name__ == "__main__":
    main()
EOF

python3 fib.py "$@"
