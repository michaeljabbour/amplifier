"""Custom Harness class that creates a cleaner directory structure."""

from terminal_bench.harness import Harness
from pathlib import Path
import shutil
from typing import Optional, List


class CleanHarness(Harness):
    """A custom Harness that creates a cleaner directory structure without nested folders."""

    def __init__(self, *args, **kwargs):
        """Initialize the harness and store the original output path."""
        self._original_output_path = kwargs.get('output_path', Path('results'))
        self._run_id = kwargs.get('run_id', '')
        super().__init__(*args, **kwargs)

    def _get_task_output_dir(self, task_id: str, attempt_num: int = 1, total_attempts: int = 1) -> Path:
        """
        Override the default task output directory creation to avoid nested folders.

        Terminal-Bench default creates: run_id/task_name/task_name.1-of-1.run_id/
        We want: run_id/task_name/
        """
        # Get the base run directory
        run_dir = self._original_output_path / self._run_id

        # Create simple task directory (no nesting)
        task_dir = run_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        return task_dir

    def run(self) -> any:
        """Run the evaluation and automatically clean up the directory structure."""
        # Run the original evaluation
        results = super().run()

        # Clean up any nested structures that were created
        self._cleanup_nested_dirs()

        return results

    def _cleanup_nested_dirs(self):
        """Clean up any nested directory structures created by Terminal-Bench."""
        run_dir = self._original_output_path / self._run_id

        if not run_dir.exists():
            return

        for task_dir in run_dir.iterdir():
            if not task_dir.is_dir():
                continue

            # Skip special directories
            if task_dir.name in ['__pycache__', '.git', '.DS_Store']:
                continue

            # Look for nested directories with pattern: task_name.X-of-Y.run_id
            nested_patterns = [
                f"{task_dir.name}.1-of-1.{self._run_id}",
                f"{task_dir.name}.1-of-1.{task_dir.name}",
                f"{task_dir.name}.{self._run_id}",
            ]

            for pattern in nested_patterns:
                nested_dir = task_dir / pattern
                if nested_dir.exists() and nested_dir.is_dir():
                    # Move all contents up one level
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
                    try:
                        nested_dir.rmdir()
                    except:
                        shutil.rmtree(nested_dir)

            # Also check for double-nested patterns (task_name/task_name/)
            double_nested = task_dir / task_dir.name
            if double_nested.exists() and double_nested.is_dir():
                # Move contents up
                for item in double_nested.iterdir():
                    dest = task_dir / item.name
                    if dest != double_nested:  # Don't move into itself
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(item), str(dest))

                # Remove the redundant directory
                try:
                    double_nested.rmdir()
                except:
                    shutil.rmtree(double_nested)


def create_harness(
    agent: str,
    task_ids: List[str],
    output_dir: Path,
    run_id: str,
    n_concurrent_trials: int = 5,
    n_attempts: int = 1,
    timeout_multiplier: float = 2.0,
    model_name: Optional[str] = None
) -> CleanHarness:
    """Create a CleanHarness instance with the given configuration."""

    # Configure agent import path
    if agent == "amplifier":
        agent_import_path = "custom_agents:CustomAmplifierAgent"
    elif agent == "baseline":
        agent_import_path = "custom_agents:ClaudeCodeAgent"
    else:
        raise ValueError(f"Unknown agent type: {agent}")

    # Initialize harness
    harness_kwargs = {
        "output_path": output_dir,
        "run_id": run_id,
        "dataset_name": "terminal-bench-core",
        "dataset_version": "0.1.1",
        "agent_import_path": agent_import_path,
        "no_rebuild": False,
        "cleanup": True,
        "task_ids": task_ids,
        "n_concurrent_trials": n_concurrent_trials,
        "n_attempts": n_attempts,
        "global_timeout_multiplier": timeout_multiplier,
    }

    if model_name:
        harness_kwargs["model_name"] = model_name

    return CleanHarness(**harness_kwargs)