#!/usr/bin/env python3
"""
Fix Docker path hardcoding in all test files.
Changes '/app/solution.sh' to use relative paths.
"""

import os
import re
from pathlib import Path

def fix_test_file(file_path):
    """Fix Docker paths in a single test file."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Check if file needs fixing
    if '/app/solution.sh' not in content:
        return False

    # Replace the Docker path with a relative path
    # The test file is in tasks/*/tests/test_outputs.py
    # The solution.sh is in tasks/*/solution.sh
    # So we need to go up one directory from tests/

    # Replace the subprocess.run line that has the hardcoded path
    old_pattern = r"\[sys\.executable, '/app/solution\.sh'([^\]]*)\]"
    new_pattern = r"[str(Path(__file__).parent.parent / 'solution.sh')\1]"

    # Also add Path import if not present
    if 'from pathlib import Path' not in content:
        content = 'from pathlib import Path\n' + content

    # Replace the pattern
    content = re.sub(old_pattern, new_pattern, content)

    # Write back
    with open(file_path, 'w') as f:
        f.write(content)

    return True

def main():
    """Fix all test files in the tasks directory."""
    tasks_dir = Path(__file__).parent / 'tasks'
    fixed_count = 0

    # Find all test_outputs.py files
    for test_file in tasks_dir.glob('*/tests/test_outputs.py'):
        print(f"Checking {test_file.parent.parent.name}/tests/test_outputs.py...")
        if fix_test_file(test_file):
            print(f"  ✅ Fixed Docker path")
            fixed_count += 1
        else:
            print(f"  ↳ No Docker path found (already fixed or different structure)")

    print(f"\n✅ Fixed {fixed_count} test files")

if __name__ == '__main__':
    main()