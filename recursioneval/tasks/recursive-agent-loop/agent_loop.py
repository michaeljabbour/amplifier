import sys
import json
import time
import re
from typing import List, Dict, Tuple

class SelfImprovingAgent:
    def __init__(self, max_iterations=5, convergence_threshold=0.05):
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.solutions = []
        self.max_depth = 0
        self.quality_scores = []

    def generate_initial_solution(self, problem: str) -> str:
        """Generate an initial baseline solution."""
        # Extract key terms from problem
        words = problem.lower().split()
        key_terms = [w for w in words if len(w) > 4]

        # Create baseline solution
        solution = f"Initial approach: Address the main aspects of '{problem}'. "
        if key_terms:
            solution += f"Focus on: {', '.join(key_terms[:3])}. "
        solution += "Steps: 1) Understand requirements, 2) Plan approach, 3) Execute solution."

        return solution

    def evaluate_quality(self, problem: str, solution: str) -> float:
        """Evaluate solution quality (0-1 scale)."""
        # Simple heuristic-based quality scoring
        score = 0.0

        # Check length (longer solutions often more complete)
        base_length_score = min(len(solution) / 300, 0.3)
        score += base_length_score

        # Check for action words (verb-based indicators of concrete steps)
        action_words = ['implement', 'execute', 'create', 'build', 'design', 'develop',
                       'analyze', 'evaluate', 'test', 'verify', 'validate', 'optimize']
        action_count = sum(1 for word in action_words if word in solution.lower())
        action_score = min(action_count / 5, 0.3)
        score += action_score

        # Check for structure indicators (numbered lists, steps, etc.)
        structure_indicators = ['step', 'phase', 'stage', 'level', 'iteration', 'approach']
        structure_count = sum(1 for indicator in structure_indicators if indicator in solution.lower())
        structure_score = min(structure_count / 4, 0.2)
        score += structure_score

        # Check for specificity (references to problem terms)
        problem_words = set(w.lower() for w in problem.split() if len(w) > 3)
        solution_words = set(w.lower() for w in solution.split() if len(w) > 3)
        overlap = len(problem_words & solution_words)
        specificity_score = min(overlap / 5, 0.2)
        score += specificity_score

        return min(round(score, 2), 1.0)

    def identify_weaknesses(self, problem: str, solution: str) -> List[str]:
        """Identify weaknesses in the current solution."""
        weaknesses = []

        # Check if solution is too generic
        if len(solution) < 100:
            weaknesses.append("Solution is too brief and lacks detail")

        # Check for missing specifics
        if "example" not in solution.lower():
            weaknesses.append("Solution lacks concrete examples")

        if "metric" not in solution.lower() and "measure" not in solution.lower():
            weaknesses.append("Solution doesn't include evaluation metrics")

        if "risk" not in solution.lower() and "challenge" not in solution.lower():
            weaknesses.append("Solution doesn't address potential challenges")

        if "resource" not in solution.lower() and "time" not in solution.lower():
            weaknesses.append("Solution doesn't address resource requirements")

        return weaknesses

    def improve_solution(self, problem: str, current_solution: str, iteration: int) -> str:
        """Generate an improved solution based on weaknesses."""
        weaknesses = self.identify_weaknesses(problem, current_solution)

        improved = current_solution + f"\n\nIteration {iteration} improvements: "

        if not weaknesses:
            improved += "Solution is comprehensive. Focus on optimization and edge cases."
        else:
            improved += "Addressing: " + "; ".join(weaknesses[:2]) + ". "

        # Add progressive enhancements
        enhancements = [
            "Enhanced with concrete examples and use cases.",
            "Added resource estimation and timeline.",
            "Included risk mitigation strategies.",
            "Optimized for scalability and maintainability.",
            "Refined with best practices and industry standards."
        ]

        if iteration - 1 < len(enhancements):
            improved += "\n" + enhancements[iteration - 1]

        return improved

    def calculate_improvement(self, prev_score: float, current_score: float) -> float:
        """Calculate improvement from previous to current score."""
        if prev_score == 0:
            return 0.0
        improvement = (current_score - prev_score) / prev_score
        return round(max(0, improvement), 2)

    def run(self, problem: str) -> Tuple[List[Dict], float, float]:
        """Run the self-improving agent loop."""
        # Generate initial solution
        current_solution = self.generate_initial_solution(problem)

        for iteration in range(1, self.max_iterations + 1):
            self.max_depth = iteration

            # Evaluate quality
            quality = self.evaluate_quality(problem, current_solution)
            self.quality_scores.append(quality)

            # Calculate improvement
            if iteration == 1:
                improvement = 0.0
            else:
                improvement = self.calculate_improvement(self.quality_scores[-2], quality)

            # Store solution
            solution_entry = {
                "iteration": iteration,
                "solution": current_solution[:200] + "..." if len(current_solution) > 200 else current_solution,
                "quality_score": quality,
                "improvement": improvement,
                "length": len(current_solution)
            }
            self.solutions.append(solution_entry)

            # Check convergence
            if iteration > 1 and improvement < self.convergence_threshold:
                # Continue for a bit longer even if converged (don't exit early)
                pass

            # Generate improved solution for next iteration
            if iteration < self.max_iterations:
                current_solution = self.improve_solution(problem, current_solution, iteration)

        # Calculate overall metrics
        total_improvement = round(self.quality_scores[-1] - self.quality_scores[0], 2)

        # Calculate convergence rate (how quickly improvements diminish)
        if len(self.quality_scores) > 1:
            improvements = []
            for i in range(1, len(self.quality_scores)):
                imp = self.calculate_improvement(self.quality_scores[i-1], self.quality_scores[i])
                improvements.append(imp)

            if improvements:
                # Convergence rate: average improvement over iterations
                convergence_rate = round(1.0 - (sum(improvements) / len(improvements)), 2)
                convergence_rate = max(0, min(1, convergence_rate))
            else:
                convergence_rate = 0.0
        else:
            convergence_rate = 0.0

        return self.solutions, total_improvement, convergence_rate

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python agent_loop.py <problem_file> [iterations]"}))
        sys.exit(1)

    problem_file = sys.argv[1]
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    if max_iterations < 1 or max_iterations > 20:
        print(json.dumps({"error": "Iterations must be between 1 and 20"}))
        sys.exit(1)

    try:
        with open(problem_file, 'r') as f:
            problem = f.read().strip()
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {problem_file}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if not problem:
        print(json.dumps({"error": "Problem text is empty"}))
        sys.exit(1)

    start_time = time.time()

    try:
        agent = SelfImprovingAgent(max_iterations=max_iterations)
        solutions, total_improvement, convergence_rate = agent.run(problem)

        elapsed_ms = (time.time() - start_time) * 1000

        output = {
            "problem": problem[:100] + "..." if len(problem) > 100 else problem,
            "iterations": max_iterations,
            "solutions": solutions,
            "total_improvement": total_improvement,
            "convergence_rate": convergence_rate,
            "max_depth": agent.max_depth,
            "execution_time_ms": round(elapsed_ms, 2)
        }

        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
