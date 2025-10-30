#!/bin/bash
set -e

# Write the nested logic resolver script
cat > logic_resolver.py << 'EOF'
import sys
import json
import time
import re

class LogicResolver:
    def __init__(self, values):
        self.values = values
        self.max_depth = 0
        self.current_depth = 0
        self.steps = []

    def record_step(self, expression, result):
        """Record an evaluation step for tracing."""
        self.steps.append({
            "expression": expression,
            "result": result,
            "depth": self.current_depth
        })

    def get_variable(self, var_name):
        """Get the value of a variable."""
        var_name = var_name.strip()
        if var_name not in self.values:
            raise ValueError(f"Undefined variable: {var_name}")
        return self.values[var_name]

    def evaluate(self, expression):
        """Recursively evaluate a logic expression."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)

        expression = expression.strip()

        # Base case: simple variable
        if not any(op in expression for op in ['AND(', 'OR(', 'NOT(', 'IF_THEN(', 'IFF(']):
            try:
                result = self.get_variable(expression)
                self.record_step(expression, result)
                self.current_depth -= 1
                return result
            except ValueError:
                self.current_depth -= 1
                raise

        # Parse and evaluate operators
        try:
            if expression.startswith('NOT(') and expression.endswith(')'):
                inner = expression[4:-1]
                inner_result = self.evaluate(inner)
                result = not inner_result
                self.record_step(expression, result)

            elif expression.startswith('AND(') and expression.endswith(')'):
                args = self._parse_args(expression[4:-1])
                result = all(self.evaluate(arg) for arg in args)
                self.record_step(expression, result)

            elif expression.startswith('OR(') and expression.endswith(')'):
                args = self._parse_args(expression[3:-1])
                result = any(self.evaluate(arg) for arg in args)
                self.record_step(expression, result)

            elif expression.startswith('IF_THEN(') and expression.endswith(')'):
                args = self._parse_args(expression[8:-1])
                if len(args) != 2:
                    raise ValueError("IF_THEN requires exactly 2 arguments")
                premise = self.evaluate(args[0])
                conclusion = self.evaluate(args[1])
                # IF_THEN is false only when premise is true and conclusion is false
                result = not premise or conclusion
                self.record_step(expression, result)

            elif expression.startswith('IFF(') and expression.endswith(')'):
                args = self._parse_args(expression[4:-1])
                if len(args) != 2:
                    raise ValueError("IFF requires exactly 2 arguments")
                left = self.evaluate(args[0])
                right = self.evaluate(args[1])
                # IFF is true when both have the same truth value
                result = left == right
                self.record_step(expression, result)

            else:
                raise ValueError(f"Invalid expression: {expression}")

            self.current_depth -= 1
            return result

        except Exception as e:
            self.current_depth -= 1
            raise

    def _parse_args(self, arg_string):
        """Parse comma-separated arguments, respecting nested parentheses."""
        args = []
        current = ""
        depth = 0

        for char in arg_string:
            if char == '(' :
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python logic_resolver.py <config_file>"}))
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Failed to read config: {str(e)}"}))
        sys.exit(1)

    # Validate config
    required_keys = {"expression", "values"}
    if not required_keys.issubset(config.keys()):
        print(json.dumps({"error": f"Missing required keys: {required_keys - set(config.keys())}"}))
        sys.exit(1)

    expression = config.get("expression", "")
    values = config.get("values", {})

    if not isinstance(expression, str):
        print(json.dumps({"error": "expression must be a string"}))
        sys.exit(1)

    if not isinstance(values, dict):
        print(json.dumps({"error": "values must be a dictionary"}))
        sys.exit(1)

    # Validate all values are booleans
    for key, value in values.items():
        if not isinstance(value, bool):
            print(json.dumps({"error": f"Value for '{key}' must be boolean, got {type(value).__name__}"}))
            sys.exit(1)

    start_time = time.time()

    try:
        resolver = LogicResolver(values)
        result = resolver.evaluate(expression)

        elapsed_ms = (time.time() - start_time) * 1000

        # Format output
        output = {
            "expression": expression,
            "result": result,
            "recursion_depth": resolver.max_depth,
            "evaluation_steps": resolver.steps,
            "execution_time_ms": round(elapsed_ms, 2)
        }

        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

python3 logic_resolver.py "$@"
