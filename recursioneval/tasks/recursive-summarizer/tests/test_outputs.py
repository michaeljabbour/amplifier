from pathlib import Path
import subprocess
import json
import sys
import os
import tempfile

def run_summarizer(text, iterations=5):
    """Run the summarizer script and return parsed JSON output."""
    # Create a temporary input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text)
        temp_file = f.name

    try:
        # Try Docker path first, then fallback to local path
        solution_path = '/app/solution.sh'
        if not os.path.exists(solution_path):
            solution_path = os.path.join(os.path.dirname(__file__), '..', 'solution.sh')

        result = subprocess.run(
            ['bash', solution_path, temp_file, str(iterations)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return json.loads(result.stdout)
    finally:
        os.unlink(temp_file)

def test_basic_summarization():
    """Test basic text summarization."""
    text = (
        "The quick brown fox jumps over the lazy dog. This is a common phrase. "
        "It has been used for many years. The fox is quick and clever. "
        "The dog is lazy and slow. They meet in the field."
    )

    output = run_summarizer(text, iterations=3)

    assert "original_text" in output, "Missing original_text"
    assert "summaries" in output, "Missing summaries"
    assert len(output["summaries"]) == 3, f"Expected 3 summaries, got {len(output['summaries'])}"

    # Check each summary
    for i, summary in enumerate(output["summaries"], 1):
        assert summary["iteration"] == i, f"Iteration mismatch at index {i}"
        assert "text" in summary, f"Missing text in iteration {i}"
        assert "length_reduction" in summary, f"Missing length_reduction in iteration {i}"
        assert "fact_retention" in summary, f"Missing fact_retention in iteration {i}"

def test_semantic_drift():
    """Test that semantic drift is calculated."""
    text = (
        "Artificial intelligence is transforming industries. Machine learning models "
        "learn patterns from data. Deep learning uses neural networks. "
        "These technologies enable automation and optimization. AI is revolutionary."
    )

    output = run_summarizer(text, iterations=5)

    assert "total_semantic_drift" in output, "Missing total_semantic_drift"
    assert 0 <= output["total_semantic_drift"] <= 1, "Semantic drift should be 0-1"

def test_fact_retention():
    """Test that fact retention decreases monotonically."""
    text = (
        "The Earth orbits the Sun. The Moon orbits the Earth. "
        "Jupiter is the largest planet. Saturn has prominent rings. "
        "Mars is called the Red Planet. Venus is hot and toxic."
    )

    output = run_summarizer(text, iterations=4)

    retentions = [s["fact_retention"] for s in output["summaries"]]

    # Check all values are between 0 and 1
    for ret in retentions:
        assert 0 <= ret <= 1, f"Fact retention {ret} out of valid range"

    # Check that retention doesn't increase (generally decreases or stays same)
    for i in range(1, len(retentions)):
        assert retentions[i] <= retentions[i-1] + 0.01, \
            f"Fact retention should not increase: {retentions}"

def test_progressive_shortening():
    """Test that summaries get progressively shorter."""
    text = (
        "Natural language processing enables computers to understand and process human language. "
        "NLP algorithms analyze text and extract meaningful information. "
        "Applications include sentiment analysis and machine translation. "
        "Named entity recognition identifies important entities in text. "
        "Dependency parsing reveals grammatical relationships. "
        "These techniques combine to create powerful language systems."
    )

    output = run_summarizer(text, iterations=5)

    lengths = [s["length"] for s in output["summaries"]]

    # Check that summaries generally get shorter (allowing for some variance)
    for i in range(1, len(lengths)):
        assert lengths[i] <= lengths[i-1], \
            f"Summary lengths should not increase: {lengths}"

def test_empty_text_error():
    """Test handling of empty input."""
    text = ""
    output = run_summarizer(text, iterations=3)
    assert "error" in output, "Should error for empty text"

def test_iteration_limits():
    """Test iteration count validation."""
    text = "The quick brown fox jumps."

    # Test valid iterations
    output = run_summarizer(text, iterations=1)
    assert "summaries" in output, "Should handle iterations=1"
    assert len(output["summaries"]) == 1

    output = run_summarizer(text, iterations=10)
    assert "summaries" in output, "Should handle iterations=10"
    assert len(output["summaries"]) == 10

def test_json_output_format():
    """Test that output is valid JSON with expected structure."""
    text = "The fox jumps. The dog runs. The cat sleeps."

    output = run_summarizer(text, iterations=2)

    assert isinstance(output, dict), "Output should be a JSON object"
    assert "original_length" in output, "Missing original_length"
    assert "iterations" in output, "Missing iterations"
    assert "max_depth" in output, "Missing max_depth"
    assert "execution_time_ms" in output, "Missing execution_time_ms"
    assert "average_fact_retention" in output, "Missing average_fact_retention"

    # Verify types
    assert isinstance(output["original_length"], int)
    assert isinstance(output["iterations"], int)
    assert isinstance(output["max_depth"], int)
    assert isinstance(output["execution_time_ms"], (int, float))
    assert isinstance(output["average_fact_retention"], (int, float))

if __name__ == "__main__":
    test_basic_summarization()
    test_semantic_drift()
    test_fact_retention()
    test_progressive_shortening()
    test_empty_text_error()
    test_iteration_limits()
    test_json_output_format()
    print("All tests passed!")
