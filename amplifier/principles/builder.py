"""Principle Builder Tool - Creates principle specifications from templates."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PrincipleTemplate:
    """Template for creating a new principle specification."""

    number: int
    name: str
    category: str
    title: str
    plain_language_definition: str
    why_it_matters: str
    implementation_approaches: list[dict] = field(default_factory=list)
    examples: list[dict] = field(default_factory=list)
    related_principles: list[int] = field(default_factory=list)
    common_pitfalls: list[str] = field(default_factory=list)
    tools_frameworks: list[str] = field(default_factory=list)
    checklist: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert template to markdown format."""
        lines = []

        # Header
        lines.append(f"# Principle #{self.number:02d} - {self.title}")
        lines.append("")

        # Plain-Language Definition
        lines.append("## Plain-Language Definition")
        lines.append("")
        lines.append(self.plain_language_definition)
        lines.append("")

        # Why This Matters
        lines.append("## Why This Matters for AI-First Development")
        lines.append("")
        lines.append(self.why_it_matters)
        lines.append("")

        # Implementation Approaches
        if self.implementation_approaches:
            lines.append("## Implementation Approaches")
            lines.append("")
            for i, approach in enumerate(self.implementation_approaches, 1):
                lines.append(f"### {i}. **{approach.get('name', 'Approach')}**")
                lines.append("")
                lines.append(approach.get('description', ''))
                lines.append("")
                if 'when_to_use' in approach:
                    lines.append(f"When to use: {approach['when_to_use']}")
                    lines.append("")
                if 'code_example' in approach:
                    lines.append("```python")
                    lines.append(approach['code_example'])
                    lines.append("```")
                    lines.append("")

        # Good vs Bad Examples
        if self.examples:
            lines.append("## Good Examples vs Bad Examples")
            lines.append("")
            for example in self.examples:
                lines.append(f"### {example.get('scenario', 'Scenario')}")
                lines.append("")
                if 'good' in example:
                    lines.append("Good:")
                    lines.append("```python")
                    lines.append(example['good'])
                    lines.append("```")
                    lines.append("")
                if 'bad' in example:
                    lines.append("Bad:")
                    lines.append("```python")
                    lines.append(example['bad'])
                    lines.append("```")
                    lines.append("")
                if 'why' in example:
                    lines.append(f"Why It Matters: {example['why']}")
                    lines.append("")

        # Related Principles
        if self.related_principles:
            lines.append("## Related Principles")
            lines.append("")
            for num in self.related_principles:
                lines.append(f"- **[Principle #{num:02d}](../#{num:02d}.md)**")
            lines.append("")

        # Common Pitfalls
        if self.common_pitfalls:
            lines.append("## Common Pitfalls")
            lines.append("")
            for i, pitfall in enumerate(self.common_pitfalls, 1):
                lines.append(f"{i}. {pitfall}")
            lines.append("")

        # Tools & Frameworks
        if self.tools_frameworks:
            lines.append("## Tools & Frameworks")
            lines.append("")
            for tool in self.tools_frameworks:
                lines.append(f"- {tool}")
            lines.append("")

        # Checklist
        if self.checklist:
            lines.append("## Self-Check Questions")
            lines.append("")
            for item in self.checklist:
                lines.append(f"- [ ] {item}")
            lines.append("")

        # References
        if self.references:
            lines.append("## References")
            lines.append("")
            for ref in self.references:
                lines.append(f"- {ref}")
            lines.append("")

        return "\n".join(lines)


class PrincipleBuilder:
    """Builder for creating and managing AI-First Principles."""

    # Category ranges based on CONTRIBUTORS.md
    CATEGORY_RANGES = {
        "people": (1, 6),
        "process": (7, 19),
        "technology": (20, 37),
        "governance": (38, 44),
        "extended_technology": (45, 52),
        "extended_process": (53, 55),
    }

    # Core principle definitions for 1-44
    CORE_PRINCIPLES = {
        # People (1-6)
        1: {"name": "small-ai-first-working-groups", "title": "Small AI-First Working Groups"},
        2: {"name": "human-ai-pairing", "title": "Human-AI Pairing"},
        3: {"name": "continuous-learning-culture", "title": "Continuous Learning Culture"},
        4: {"name": "ai-literacy-training", "title": "AI Literacy Training"},
        5: {"name": "trust-through-transparency", "title": "Trust Through Transparency"},
        6: {"name": "collaborative-ownership", "title": "Collaborative Ownership"},

        # Process (7-19)
        7: {"name": "test-driven-prompting", "title": "Test-Driven Prompting"},
        8: {"name": "iterative-refinement", "title": "Iterative Refinement"},
        9: {"name": "version-control-everything", "title": "Version Control Everything"},
        10: {"name": "continuous-evaluation", "title": "Continuous Evaluation"},
        11: {"name": "feedback-loops", "title": "Feedback Loops"},
        12: {"name": "documentation-first", "title": "Documentation First"},
        13: {"name": "progressive-enhancement", "title": "Progressive Enhancement"},
        14: {"name": "fail-fast-learn-faster", "title": "Fail Fast, Learn Faster"},
        15: {"name": "automated-workflows", "title": "Automated Workflows"},
        16: {"name": "context-preservation", "title": "Context Preservation"},
        17: {"name": "incremental-adoption", "title": "Incremental Adoption"},
        18: {"name": "measurement-driven", "title": "Measurement Driven"},
        19: {"name": "collaborative-review", "title": "Collaborative Review"},

        # Technology (20-37)
        20: {"name": "modular-prompts", "title": "Modular Prompts"},
        21: {"name": "semantic-versioning", "title": "Semantic Versioning"},
        22: {"name": "api-first-design", "title": "API-First Design"},
        23: {"name": "observability-by-design", "title": "Observability by Design"},
        24: {"name": "deterministic-outputs", "title": "Deterministic Outputs"},
        25: {"name": "graceful-degradation", "title": "Graceful Degradation"},
        26: {"name": "idempotency-by-design", "title": "Idempotency by Design"},
        27: {"name": "caching-strategies", "title": "Caching Strategies"},
        28: {"name": "rate-limiting", "title": "Rate Limiting"},
        29: {"name": "circuit-breakers", "title": "Circuit Breakers"},
        30: {"name": "structured-outputs", "title": "Structured Outputs"},
        31: {"name": "schema-validation", "title": "Schema Validation"},
        32: {"name": "error-recovery", "title": "Error Recovery"},
        33: {"name": "stateless-design", "title": "Stateless Design"},
        34: {"name": "token-optimization", "title": "Token Optimization"},
        35: {"name": "parallel-processing", "title": "Parallel Processing"},
        36: {"name": "streaming-responses", "title": "Streaming Responses"},
        37: {"name": "hybrid-architectures", "title": "Hybrid Architectures"},

        # Governance (38-44)
        38: {"name": "ethical-guidelines", "title": "Ethical Guidelines"},
        39: {"name": "bias-detection", "title": "Bias Detection"},
        40: {"name": "privacy-by-design", "title": "Privacy by Design"},
        41: {"name": "compliance-automation", "title": "Compliance Automation"},
        42: {"name": "audit-trails", "title": "Audit Trails"},
        43: {"name": "cost-management", "title": "Cost Management"},
        44: {"name": "quality-gates", "title": "Quality Gates"},
    }

    def __init__(self, output_dir: Path = None):
        """Initialize the principle builder."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / ".amplifier" / "ai-first-principles" / "principles"
        self.output_dir = output_dir

    def get_category(self, number: int) -> str:
        """Determine category based on principle number."""
        if 1 <= number <= 6:
            return "people"
        elif 7 <= number <= 19:
            return "process"
        elif 20 <= number <= 37 or 45 <= number <= 52:
            return "technology"
        elif 38 <= number <= 44:
            return "governance"
        elif 53 <= number <= 55:
            return "process"
        else:
            return "unknown"

    def create_principle(self, number: int, name: str = None, title: str = None) -> PrincipleTemplate:
        """Create a principle template with basic structure."""
        if name is None or title is None:
            # Use predefined if available
            if number in self.CORE_PRINCIPLES:
                info = self.CORE_PRINCIPLES[number]
                name = name or info["name"]
                title = title or info["title"]
            else:
                raise ValueError(f"No predefined principle for number {number}")

        category = self.get_category(number)

        # Create basic template
        template = PrincipleTemplate(
            number=number,
            name=name,
            category=category,
            title=title,
            plain_language_definition=f"{title} ensures that AI-first development follows best practices for {category}. This principle guides teams to implement effective patterns that improve system reliability and maintainability.",
            why_it_matters=f"""AI-first development introduces unique challenges in {category} that traditional approaches don't address. {title} provides a framework for handling these challenges effectively.

1. **Improved reliability**: Systems built with this principle are more robust and predictable
2. **Better maintainability**: Teams can understand and modify the system more easily
3. **Enhanced scalability**: The approach scales with growing complexity

Without {title}, teams risk building systems that become increasingly difficult to manage and evolve.""",
            implementation_approaches=[
                {
                    "name": f"Basic {title} Implementation",
                    "description": f"Start with a simple implementation of {title} that addresses core requirements.",
                    "when_to_use": "Use this approach when beginning a new project or introducing the principle to an existing system.",
                    "code_example": f"""# Example implementation
def implement_{name.replace('-', '_')}():
    \"\"\"Basic implementation of {title}.\"\"\"
    # Implementation details here
    pass"""
                }
            ],
            common_pitfalls=[
                f"Over-engineering the {title} implementation",
                "Not considering edge cases and failure modes",
                "Insufficient testing of the approach",
            ],
            checklist=[
                f"Have you implemented {title} according to best practices?",
                "Are all team members familiar with this principle?",
                "Is the implementation tested and documented?",
            ]
        )

        return template

    def save_principle(self, template: PrincipleTemplate) -> Path:
        """Save a principle template to markdown file."""
        # Create category directory if needed
        category_dir = self.output_dir / template.category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Create file path
        filename = f"{template.number:02d}-{template.name}.md"
        filepath = category_dir / filename

        # Write markdown content
        content = template.to_markdown()
        filepath.write_text(content, encoding="utf-8")

        logger.info(f"Created principle: {filepath}")
        return filepath

    def create_all_missing_principles(self) -> list[Path]:
        """Create all missing principles (1-44)."""
        created_files = []

        for number in range(1, 45):
            try:
                template = self.create_principle(number)
                filepath = self.save_principle(template)
                created_files.append(filepath)
            except Exception as e:
                logger.error(f"Failed to create principle {number}: {e}")

        return created_files

    def create_template_file(self) -> Path:
        """Create a TEMPLATE.md file for reference."""
        template_path = self.output_dir.parent / "TEMPLATE.md"

        content = """# Principle #{number} - {Title}

## Plain-Language Definition

{1-2 sentences that explain the principle in simple terms without jargon}

## Why This Matters for AI-First Development

{2-3 paragraphs explaining:
1. Problem context - what unique challenges AI-first introduces
2. Specific benefits - how this principle addresses those challenges (numbered list of 3)
3. Consequences - what happens when violated}

## Implementation Approaches

### 1. **{Approach Name}**

{Description of the approach in 2-3 sentences}

When to use: {Specific scenario where this approach shines}

```python
# Working code example
def example_implementation():
    pass
```

### 2. **{Another Approach}**

{Description}

When to use: {Scenario}

## Good Examples vs Bad Examples

### {Scenario Name}

Good:
```python
# Complete, runnable code
```

Bad:
```python
# Complete, runnable anti-pattern
```

Why It Matters: {Concrete impact explanation}

## Related Principles

- **[Principle #{num} - {Name}](path/to/spec.md)** - {Relationship explanation}

## Common Pitfalls

1. {Pitfall description}
2. {Another pitfall}
3. {Third pitfall}

## Tools & Frameworks

- {Tool or framework that supports this principle}
- {Another tool}

## Self-Check Questions

- [ ] {Question to verify correct implementation}
- [ ] {Another verification question}
- [ ] {Third question}

## References

- {Academic paper, blog post, or authoritative source}
- {Another reference}
"""
        template_path.write_text(content, encoding="utf-8")
        logger.info(f"Created template: {template_path}")
        return template_path


if __name__ == "__main__":
    # Example usage
    builder = PrincipleBuilder()

    # Create all missing principles
    print("Creating missing principles 1-44...")
    created = builder.create_all_missing_principles()
    print(f"Created {len(created)} principle files")

    # Create template file
    builder.create_template_file()
    print("Created TEMPLATE.md")