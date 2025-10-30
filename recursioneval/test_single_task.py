#!/usr/bin/env python3
"""Test script to run a single terminal-bench task for verification."""

import json
from datetime import datetime
from pathlib import Path

from terminal_bench import Harness

def main():
    run_id = datetime.now().strftime("%Y-%m-%d__%H-%M-%S-test")
    runs_dir = Path(__file__).parents[2] / "ai_working" / "tmp"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # Test with just one easy task
    task_ids = ["csv-to-parquet"]

    # Use the amplifier agent for testing
    agent_import_path = "custom_agents:CustomAmplifierAgent"

    print(f"🧪 Testing terminal-bench with task: {task_ids[0]}")
    print(f"📁 Output directory: {runs_dir / run_id}")

    harness = Harness(
        output_path=runs_dir,
        run_id=run_id,
        dataset_name="terminal-bench-core",
        dataset_version="0.1.1",
        agent_import_path=agent_import_path,
        no_rebuild=False,
        cleanup=True,
        task_ids=task_ids,
        n_concurrent_trials=1,
        n_attempts=1,
        global_timeout_multiplier=2,
    )

    results = harness.run()

    # Pretty print the results
    print("\n🎯 Test Results:")
    print(json.dumps(results, indent=2))

    # Check if the task succeeded
    if results and len(results) > 0:
        task_result = results[0]
        success = task_result.get("success", False)
        if success:
            print("\n✅ Test passed! Terminal-bench is working correctly.")
        else:
            print("\n⚠️ Task failed, but terminal-bench is running.")
    else:
        print("\n❌ No results returned - check configuration.")

    return results

if __name__ == "__main__":
    main()