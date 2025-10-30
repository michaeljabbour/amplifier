#!/usr/bin/env python3
"""
Reasoning Trace Analyzer for Terminal-Bench Evaluation

This module analyzes HOW agents solve tasks, extracting patterns from their
reasoning processes to understand the mechanisms behind success and failure.
"""

import re
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime


@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process."""
    step_id: int
    timestamp: str
    action_type: str  # plan, tool_use, error, backtrack, success
    tool_name: Optional[str]
    content: str
    success: bool
    parent_step: Optional[int] = None
    children_steps: List[int] = field(default_factory=list)


@dataclass
class ReasoningPattern:
    """Represents a pattern found in reasoning."""
    pattern_type: str
    frequency: int
    avg_success_rate: float
    examples: List[str]
    description: str


class ReasoningTraceAnalyzer:
    """Analyze reasoning patterns from agent execution logs."""

    TOOL_PATTERNS = {
        'exploration': ['Read', 'Glob', 'Grep', 'LS'],
        'modification': ['Edit', 'Write', 'NotebookEdit'],
        'execution': ['Bash', 'Agent'],
        'planning': ['TodoWrite', 'TodoRead'],
        'research': ['WebFetch', 'WebSearch', 'mcp__deepwiki']
    }

    THINKING_INDICATORS = [
        r'/ultrathink-task',
        r'Let me think',
        r'I need to',
        r'First,? I',
        r'I\'ll start by',
        r'Breaking this down',
        r'The plan is'
    ]

    ERROR_PATTERNS = [
        r'error:',
        r'failed:',
        r'Error:',
        r'Failed:',
        r'Exception:',
        r'Traceback'
    ]

    def __init__(self):
        """Initialize the analyzer."""
        self.reasoning_graphs = {}
        self.pattern_library = defaultdict(list)
        self.success_patterns = []
        self.failure_patterns = []

    def analyze_log(self, log_path: Path, task_id: str) -> Dict[str, Any]:
        """Analyze a single agent log file."""
        with open(log_path, 'r') as f:
            content = f.read()

        # Extract reasoning steps
        steps = self.extract_reasoning_steps(content)

        # Build reasoning graph
        graph = self.build_reasoning_graph(steps)

        # Analyze patterns
        patterns = {
            'planning_depth': self.measure_planning_depth(steps),
            'backtrack_count': self.count_backtracks(steps),
            'error_recovery_rate': self.calculate_error_recovery(steps),
            'tool_sequence_complexity': self.analyze_tool_sequences(steps),
            'reasoning_loops': self.detect_reasoning_loops(graph),
            'decision_points': self.identify_decision_points(steps),
            'context_switches': self.count_context_switches(steps)
        }

        # Store for pattern mining
        self.reasoning_graphs[task_id] = graph

        return {
            'task_id': task_id,
            'total_steps': len(steps),
            'unique_tools_used': self.count_unique_tools(steps),
            'patterns': patterns,
            'graph_metrics': self.calculate_graph_metrics(graph),
            'reasoning_efficiency': self.calculate_reasoning_efficiency(steps, patterns)
        }

    def extract_reasoning_steps(self, log_content: str) -> List[ReasoningStep]:
        """Extract structured reasoning steps from log."""
        steps = []
        step_id = 0

        # Split log into logical chunks (tool calls, responses, etc.)
        lines = log_content.split('\n')
        current_tool = None
        current_content = []

        for line in lines:
            # Detect tool invocation
            tool_match = re.search(r'Tool:\s*(\w+)', line)
            if tool_match:
                # Save previous step if exists
                if current_content:
                    steps.append(ReasoningStep(
                        step_id=step_id,
                        timestamp=self._extract_timestamp(line),
                        action_type='tool_use',
                        tool_name=current_tool,
                        content='\n'.join(current_content),
                        success=not any(re.search(p, '\n'.join(current_content))
                                       for p in self.ERROR_PATTERNS)
                    ))
                    step_id += 1

                current_tool = tool_match.group(1)
                current_content = [line]

            # Detect thinking/planning
            elif any(re.search(pattern, line) for pattern in self.THINKING_INDICATORS):
                if current_content:
                    steps.append(ReasoningStep(
                        step_id=step_id,
                        timestamp=self._extract_timestamp(line),
                        action_type='plan',
                        tool_name=None,
                        content='\n'.join(current_content),
                        success=True
                    ))
                    step_id += 1
                    current_content = []

            # Detect errors
            elif any(re.search(pattern, line) for pattern in self.ERROR_PATTERNS):
                steps.append(ReasoningStep(
                    step_id=step_id,
                    timestamp=self._extract_timestamp(line),
                    action_type='error',
                    tool_name=current_tool,
                    content=line,
                    success=False
                ))
                step_id += 1

            else:
                current_content.append(line)

        return steps

    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line if present."""
        timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', line)
        return timestamp_match.group(0) if timestamp_match else ""

    def build_reasoning_graph(self, steps: List[ReasoningStep]) -> nx.DiGraph:
        """Build directed graph of reasoning flow."""
        G = nx.DiGraph()

        for i, step in enumerate(steps):
            # Add node with attributes
            G.add_node(step.step_id,
                      action_type=step.action_type,
                      tool=step.tool_name,
                      success=step.success)

            # Add edge from previous step
            if i > 0:
                G.add_edge(steps[i-1].step_id, step.step_id)

            # Detect backtracking (returning to earlier patterns)
            if step.action_type == 'error' and i < len(steps) - 1:
                # Look for retry patterns
                for j in range(i+1, min(i+5, len(steps))):
                    if steps[j].tool_name == step.tool_name:
                        G.add_edge(step.step_id, steps[j].step_id, edge_type='retry')

        return G

    def measure_planning_depth(self, steps: List[ReasoningStep]) -> int:
        """Measure the depth of planning/decomposition."""
        planning_steps = [s for s in steps if s.action_type == 'plan']

        if not planning_steps:
            return 0

        # Look for hierarchical planning indicators
        depth = 1
        for step in planning_steps:
            # Count nested planning levels
            indent_level = len(re.findall(r'^\s{2,}-', step.content, re.MULTILINE))
            depth = max(depth, indent_level)

        return depth

    def count_backtracks(self, steps: List[ReasoningStep]) -> int:
        """Count number of backtracks/retries."""
        backtracks = 0
        tool_history = []

        for step in steps:
            if step.tool_name:
                if step.tool_name in tool_history[-3:] and not step.success:
                    backtracks += 1
                tool_history.append(step.tool_name)

        return backtracks

    def calculate_error_recovery(self, steps: List[ReasoningStep]) -> float:
        """Calculate error recovery rate."""
        error_indices = [i for i, s in enumerate(steps) if s.action_type == 'error']

        if not error_indices:
            return 1.0  # No errors to recover from

        recovered = 0
        for error_idx in error_indices:
            # Check if there's a successful action within next 5 steps
            for j in range(error_idx + 1, min(error_idx + 6, len(steps))):
                if steps[j].success:
                    recovered += 1
                    break

        return recovered / len(error_indices) if error_indices else 0

    def analyze_tool_sequences(self, steps: List[ReasoningStep]) -> Dict[str, Any]:
        """Analyze complexity of tool usage sequences."""
        tool_sequence = [s.tool_name for s in steps if s.tool_name]

        # Calculate sequence metrics
        unique_tools = len(set(tool_sequence))
        total_tools = len(tool_sequence)

        # Find common patterns
        bigrams = [(tool_sequence[i], tool_sequence[i+1])
                  for i in range(len(tool_sequence)-1)]
        trigrams = [(tool_sequence[i], tool_sequence[i+1], tool_sequence[i+2])
                   for i in range(len(tool_sequence)-2)]

        return {
            'unique_tools': unique_tools,
            'total_tool_calls': total_tools,
            'tool_diversity': unique_tools / total_tools if total_tools > 0 else 0,
            'most_common_bigrams': Counter(bigrams).most_common(3),
            'most_common_trigrams': Counter(trigrams).most_common(3),
            'tool_categories_used': self._categorize_tools(tool_sequence)
        }

    def _categorize_tools(self, tool_sequence: List[str]) -> Dict[str, int]:
        """Categorize tools used."""
        category_counts = defaultdict(int)

        for tool in tool_sequence:
            if not tool:
                continue
            for category, tools in self.TOOL_PATTERNS.items():
                if tool in tools:
                    category_counts[category] += 1
                    break
            else:
                category_counts['other'] += 1

        return dict(category_counts)

    def detect_reasoning_loops(self, graph: nx.DiGraph) -> int:
        """Detect loops in reasoning (revisiting same decisions)."""
        try:
            cycles = list(nx.simple_cycles(graph))
            return len(cycles)
        except:
            return 0

    def identify_decision_points(self, steps: List[ReasoningStep]) -> List[int]:
        """Identify critical decision points in reasoning."""
        decision_points = []

        for i, step in enumerate(steps):
            # Look for branching indicators
            if 'if' in step.content.lower() or 'else' in step.content.lower():
                decision_points.append(i)
            # Look for alternative considerations
            elif any(word in step.content.lower()
                    for word in ['alternatively', 'instead', 'or we could']):
                decision_points.append(i)

        return decision_points

    def count_context_switches(self, steps: List[ReasoningStep]) -> int:
        """Count major context switches in reasoning."""
        switches = 0
        prev_category = None

        for step in steps:
            if step.tool_name:
                current_category = None
                for category, tools in self.TOOL_PATTERNS.items():
                    if step.tool_name in tools:
                        current_category = category
                        break

                if prev_category and current_category != prev_category:
                    switches += 1
                prev_category = current_category

        return switches

    def count_unique_tools(self, steps: List[ReasoningStep]) -> int:
        """Count unique tools used."""
        tools = set(s.tool_name for s in steps if s.tool_name)
        return len(tools)

    def calculate_graph_metrics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Calculate graph-theoretic metrics of reasoning."""
        if len(graph) == 0:
            return {}

        metrics = {
            'num_nodes': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'density': nx.density(graph),
            'is_dag': nx.is_directed_acyclic_graph(graph),
            'longest_path': self._find_longest_path(graph)
        }

        # Add centrality measures if graph is large enough
        if len(graph) > 3:
            try:
                metrics['avg_degree'] = sum(dict(graph.degree()).values()) / len(graph)
                metrics['max_degree'] = max(dict(graph.degree()).values())
            except:
                pass

        return metrics

    def _find_longest_path(self, graph: nx.DiGraph) -> int:
        """Find longest path in DAG."""
        if not nx.is_directed_acyclic_graph(graph):
            return 0

        try:
            return len(nx.dag_longest_path(graph))
        except:
            return 0

    def calculate_reasoning_efficiency(self, steps: List[ReasoningStep],
                                      patterns: Dict) -> float:
        """Calculate overall reasoning efficiency score."""
        efficiency_score = 1.0

        # Penalize backtracks
        efficiency_score -= patterns['backtrack_count'] * 0.05

        # Penalize reasoning loops
        efficiency_score -= patterns['reasoning_loops'] * 0.1

        # Penalize context switches
        efficiency_score -= patterns['context_switches'] * 0.02

        # Reward error recovery
        efficiency_score += patterns['error_recovery_rate'] * 0.2

        # Reward planning depth
        efficiency_score += min(patterns['planning_depth'] * 0.1, 0.3)

        return max(0, min(1, efficiency_score))

    def visualize_reasoning_graph(self, task_id: str, output_path: Optional[Path] = None):
        """Create visual representation of reasoning graph."""
        if task_id not in self.reasoning_graphs:
            print(f"No graph found for task {task_id}")
            return

        graph = self.reasoning_graphs[task_id]

        plt.figure(figsize=(12, 8))

        # Create layout
        pos = nx.spring_layout(graph, k=2, iterations=50)

        # Color nodes by action type
        color_map = {
            'plan': 'lightblue',
            'tool_use': 'lightgreen',
            'error': 'lightcoral',
            'backtrack': 'yellow',
            'success': 'lime'
        }

        node_colors = [color_map.get(graph.nodes[node].get('action_type', 'plan'), 'gray')
                      for node in graph.nodes()]

        # Draw graph
        nx.draw(graph, pos, node_color=node_colors, with_labels=True,
               node_size=500, font_size=8, font_weight='bold',
               arrows=True, arrowsize=20)

        # Add legend
        legend_elements = [plt.scatter([], [], c=color, s=100, label=action)
                          for action, color in color_map.items()]
        plt.legend(handles=legend_elements, loc='upper right')

        plt.title(f"Reasoning Graph for Task: {task_id}")
        plt.axis('off')

        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()

        plt.close()

    def mine_success_patterns(self, successful_traces: List[Dict]) -> List[ReasoningPattern]:
        """Mine common patterns from successful task completions."""
        patterns = []

        # Analyze tool sequences
        successful_sequences = []
        for trace in successful_traces:
            steps = trace.get('steps', [])
            sequence = [s.tool_name for s in steps if s.tool_name]
            successful_sequences.append(sequence)

        # Find common subsequences
        common_patterns = self._find_common_subsequences(successful_sequences)

        for pattern, frequency in common_patterns.items():
            patterns.append(ReasoningPattern(
                pattern_type='tool_sequence',
                frequency=frequency,
                avg_success_rate=1.0,  # These are from successful traces
                examples=pattern,
                description=f"Common successful tool sequence: {' -> '.join(pattern)}"
            ))

        return patterns

    def _find_common_subsequences(self, sequences: List[List[str]],
                                 min_length: int = 2) -> Dict[Tuple[str], int]:
        """Find common subsequences in tool usage."""
        subsequence_counts = defaultdict(int)

        for sequence in sequences:
            for length in range(min_length, min(len(sequence), 5)):
                for i in range(len(sequence) - length + 1):
                    subsequence = tuple(sequence[i:i+length])
                    subsequence_counts[subsequence] += 1

        # Filter to only common patterns (appearing in >20% of sequences)
        threshold = len(sequences) * 0.2
        common = {seq: count for seq, count in subsequence_counts.items()
                 if count >= threshold}

        return common

    def generate_trace_report(self, analysis_results: Dict) -> str:
        """Generate detailed report of reasoning trace analysis."""
        report = []
        report.append("# Reasoning Trace Analysis Report")
        report.append(f"\nTask ID: {analysis_results['task_id']}")
        report.append(f"Total Reasoning Steps: {analysis_results['total_steps']}")

        report.append("\n## Reasoning Patterns")
        patterns = analysis_results['patterns']
        report.append(f"- Planning Depth: {patterns['planning_depth']}")
        report.append(f"- Backtrack Count: {patterns['backtrack_count']}")
        report.append(f"- Error Recovery Rate: {patterns['error_recovery_rate']:.2%}")
        report.append(f"- Context Switches: {patterns['context_switches']}")
        report.append(f"- Reasoning Loops: {patterns['reasoning_loops']}")

        report.append("\n## Tool Usage Analysis")
        tool_analysis = patterns['tool_sequence_complexity']
        report.append(f"- Unique Tools: {tool_analysis['unique_tools']}")
        report.append(f"- Total Tool Calls: {tool_analysis['total_tool_calls']}")
        report.append(f"- Tool Diversity: {tool_analysis['tool_diversity']:.2f}")

        report.append("\n### Tool Categories Used:")
        for category, count in tool_analysis['tool_categories_used'].items():
            report.append(f"  - {category}: {count}")

        report.append("\n## Graph Metrics")
        graph_metrics = analysis_results['graph_metrics']
        if graph_metrics:
            report.append(f"- Nodes: {graph_metrics.get('num_nodes', 0)}")
            report.append(f"- Edges: {graph_metrics.get('num_edges', 0)}")
            report.append(f"- Longest Path: {graph_metrics.get('longest_path', 0)}")
            report.append(f"- Is DAG: {graph_metrics.get('is_dag', False)}")

        report.append(f"\n## Reasoning Efficiency Score: {analysis_results['reasoning_efficiency']:.2f}/1.00")

        return "\n".join(report)


def main():
    """Example usage of reasoning trace analyzer."""
    analyzer = ReasoningTraceAnalyzer()

    # Example: Analyze a log file
    # log_path = Path("ai_working/tmp/amplifier_train/task_id/agent.log")
    # analysis = analyzer.analyze_log(log_path, "task_id")

    # Generate report
    # report = analyzer.generate_trace_report(analysis)
    # print(report)

    # Visualize reasoning graph
    # analyzer.visualize_reasoning_graph("task_id", Path("reasoning_graph.png"))

    print("Reasoning Trace Analyzer Ready")
    print("Use: analyzer.analyze_log(log_path, task_id)")
    print("Then: analyzer.visualize_reasoning_graph(task_id)")


if __name__ == "__main__":
    main()