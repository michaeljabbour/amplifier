import sys
import json
import time
import re
from collections import Counter

class RecursiveSummarizer:
    def __init__(self, iterations=5):
        self.iterations = iterations
        self.summaries = []
        self.max_depth = 0
        self.original_entities = set()

    def extract_sentences(self, text):
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def extract_entities(self, text):
        """Extract key entities (capitalized words and important terms)."""
        words = text.split()
        # Simple entity extraction: capitalized words and common important terms
        entities = set()
        for word in words:
            # Keep proper nouns and important words
            if word and word[0].isupper() and len(word) > 2:
                entities.add(word.lower())
        return entities

    def calculate_fact_retention(self, original_entities, current_entities):
        """Calculate what percentage of original entities are retained."""
        if not original_entities:
            return 1.0
        common = len(original_entities & current_entities)
        return round(common / len(original_entities), 2)

    def calculate_semantic_drift(self, original_text, final_text):
        """Estimate semantic drift using word overlap."""
        original_words = set(original_text.lower().split())
        final_words = set(final_text.lower().split())

        if not original_words:
            return 0.0

        common = len(original_words & final_words)
        union = len(original_words | final_words)

        # Jaccard similarity
        similarity = common / union if union > 0 else 0
        drift = round(1.0 - similarity, 2)
        return drift

    def summarize_iteration(self, text, iteration):
        """Summarize text in a single iteration."""
        sentences = self.extract_sentences(text)

        if not sentences or len(sentences) <= 1:
            return text

        # Keep approximately 70% of sentences (round down)
        keep_count = max(1, len(sentences) * 70 // 100)

        # Simple heuristic: keep sentences with most entities
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            entities = self.extract_entities(sentence)
            score = len(entities) + (1 / (i + 1))  # Slight bias toward first sentences
            scored_sentences.append((score, sentence))

        # Sort by score and keep top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        selected = sorted(scored_sentences[:keep_count], key=lambda x: sentences.index(x[1]))

        summary = '. '.join([s[1] for s in selected])
        if summary and not summary.endswith('.'):
            summary += '.'

        return summary

    def run(self, text):
        """Run recursive summarization."""
        self.original_entities = self.extract_entities(text)
        current_text = text

        for i in range(1, self.iterations + 1):
            self.max_depth = i
            previous_length = len(current_text)

            # Summarize
            current_text = self.summarize_iteration(current_text, i)
            new_length = len(current_text)

            # Calculate metrics
            current_entities = self.extract_entities(current_text)
            fact_retention = self.calculate_fact_retention(self.original_entities, current_entities)
            length_reduction = round(1.0 - (new_length / previous_length), 2) if previous_length > 0 else 0

            summary_entry = {
                "iteration": i,
                "text": current_text[:200] + "..." if len(current_text) > 200 else current_text,
                "length": new_length,
                "length_reduction": length_reduction,
                "fact_retention": fact_retention,
                "entity_count": len(current_entities)
            }
            self.summaries.append(summary_entry)

        return self.summaries

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python summarizer.py <input_file> [iterations]"}))
        sys.exit(1)

    input_file = sys.argv[1]
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    if iterations < 1 or iterations > 20:
        print(json.dumps({"error": "Iterations must be between 1 and 20"}))
        sys.exit(1)

    try:
        with open(input_file, 'r') as f:
            text = f.read().strip()
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {input_file}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if not text:
        print(json.dumps({"error": "Input text is empty"}))
        sys.exit(1)

    start_time = time.time()

    try:
        summarizer = RecursiveSummarizer(iterations)
        summaries = summarizer.run(text)

        # Calculate overall metrics
        fact_retentions = [s["fact_retention"] for s in summaries]
        total_semantic_drift = summarizer.calculate_semantic_drift(text, summaries[-1]["text"])
        average_fact_retention = round(sum(fact_retentions) / len(fact_retentions), 2)

        elapsed_ms = (time.time() - start_time) * 1000

        output = {
            "original_text": text[:200] + "..." if len(text) > 200 else text,
            "original_length": len(text),
            "iterations": iterations,
            "summaries": summaries,
            "total_semantic_drift": total_semantic_drift,
            "average_fact_retention": average_fact_retention,
            "max_depth": summarizer.max_depth,
            "execution_time_ms": round(elapsed_ms, 2)
        }

        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
