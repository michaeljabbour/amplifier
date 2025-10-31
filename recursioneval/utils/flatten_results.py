#!/usr/bin/env python3
"""
Flatten Terminal-Bench's nested results structure.

Terminal-Bench creates:
  results/run_id/task_name/task_name.1-of-1.run_id/files

We want:
  results/run_id/task_name/files
"""

import os
import shutil
from pathlib import Path
import sys


def flatten_results_structure(results_dir: Path, run_id: str = None):
    """
    Flatten the nested folder structure created by Terminal-Bench.

    Args:
        results_dir: Base results directory
        run_id: Specific run to flatten (if None, process latest)
    """
    # Find run directory
    if run_id:
        run_dir = results_dir / run_id
    else:
        # Find latest run
        run_dirs = [d for d in results_dir.glob("amplifier_*") if d.is_dir()]
        if not run_dirs:
            print("No run directories found")
            return
        run_dir = max(run_dirs, key=lambda x: x.stat().st_mtime)
        run_id = run_dir.name

    if not run_dir.exists():
        print(f"Run directory not found: {run_dir}")
        return

    print(f"📁 Flattening structure for: {run_id}")

    # Process each task directory
    tasks_processed = 0
    for task_dir in run_dir.iterdir():
        if not task_dir.is_dir():
            continue

        if task_dir.name in ['__pycache__', '.git']:
            continue

        # Look for nested directories with the pattern task_name.X-of-Y.run_id
        nested_dirs = list(task_dir.glob(f"{task_dir.name}*{run_id}"))

        if nested_dirs:
            # Found nested structure - flatten it
            nested_dir = nested_dirs[0]

            # Move contents up one level
            for item in nested_dir.iterdir():
                dest = task_dir / item.name

                # Remove destination if it exists
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()

                # Move item to parent directory
                shutil.move(str(item), str(dest))

            # Remove the now-empty nested directory
            nested_dir.rmdir()

            tasks_processed += 1
            print(f"  ✓ Flattened: {task_dir.name}")

    print(f"\n✅ Processed {tasks_processed} tasks")

    # Update paths in results.json if it exists
    results_json = run_dir / "results.json"
    if results_json.exists():
        import json

        with open(results_json, 'r') as f:
            data = json.load(f)

        # Update any paths that reference the nested structure
        modified = False
        if 'results' in data:
            for result in data['results']:
                if 'workspace_dir' in result:
                    old_path = result['workspace_dir']
                    # Remove the nested part from the path
                    if f".{run_id}" in old_path:
                        parts = old_path.split('/')
                        # Find and remove the redundant nested directory
                        new_parts = []
                        skip_next = False
                        for i, part in enumerate(parts):
                            if skip_next:
                                skip_next = False
                                continue
                            if run_id in part and i > 0 and parts[i-1] in part:
                                # This is the redundant nested directory
                                continue
                            new_parts.append(part)
                        result['workspace_dir'] = '/'.join(new_parts)
                        modified = True

        if modified:
            with open(results_json, 'w') as f:
                json.dump(data, f, indent=2)
            print("📝 Updated paths in results.json")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Flatten Terminal-Bench nested results structure"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).parent.parent / "results",
        help="Results directory (default: results/)"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        help="Specific run ID to flatten (default: latest)"
    )

    args = parser.parse_args()

    try:
        flatten_results_structure(args.results_dir, args.run_id)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())