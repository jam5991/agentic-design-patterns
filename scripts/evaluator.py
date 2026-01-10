"""
Evaluator for OpenEvolve Evolution
==================================
This module defines the evaluation function that scores evolved programs.
OpenEvolve uses this to determine which program variants are better.

The evaluator returns a dictionary of metrics that OpenEvolve uses for
multi-objective optimization.

IMPORTANT: OpenEvolve passes a FILE PATH to the evaluate function, not a module.
"""

import time
import random
import importlib.util
import sys
from pathlib import Path
from typing import Any


def evaluate(program_path: str) -> dict[str, float]:
    """
    Evaluate an evolved program and return performance metrics.
    
    This function is called by OpenEvolve to score each candidate program.
    It should return a dictionary of metric names to scores, where higher
    scores are better.
    
    Args:
        program_path: Path to the evolved program file
        
    Returns:
        Dictionary of metric names to scores (higher is better)
    """
    metrics = {}
    
    # Load the program module from the file path
    program_module = _load_module(program_path)
    
    if program_module is None:
        # Failed to load module - return zero scores
        return {
            "correctness": 0.0,
            "performance": 0.0,
            "combined_score": 0.0
        }
    
    # Test correctness on various inputs
    correctness_score = _test_correctness(program_module)
    metrics["correctness"] = correctness_score
    
    # Test performance (speed)
    performance_score = _test_performance(program_module)
    metrics["performance"] = performance_score
    
    # Combined score for overall fitness (required by OpenEvolve)
    metrics["combined_score"] = (correctness_score * 0.7) + (performance_score * 0.3)
    
    return metrics


def _load_module(program_path: str) -> Any:
    """Load a Python module from a file path."""
    try:
        spec = importlib.util.spec_from_file_location("evolved_program", program_path)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules["evolved_program"] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module from {program_path}: {e}")
        return None


def _test_correctness(program_module: Any) -> float:
    """Test if the sorting function produces correct results."""
    # Check if the module has sort_numbers function
    if not hasattr(program_module, "sort_numbers"):
        return 0.0
    
    test_cases = [
        [],
        [1],
        [2, 1],
        [3, 1, 2],
        [5, 4, 3, 2, 1],
        list(range(10, 0, -1)),
        [random.randint(0, 100) for _ in range(20)],
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_input in test_cases:
        try:
            result = program_module.sort_numbers(test_input.copy())
            expected = sorted(test_input)
            if result == expected:
                passed += 1
        except Exception:
            pass  # Failed test
    
    return passed / total if total > 0 else 0.0


def _test_performance(program_module: Any) -> float:
    """Test the performance (speed) of the sorting function."""
    # Check if the module has sort_numbers function
    if not hasattr(program_module, "sort_numbers"):
        return 0.0
    
    # Generate test data
    test_data = [random.randint(0, 10000) for _ in range(1000)]
    
    try:
        # Time the execution
        start_time = time.perf_counter()
        for _ in range(10):  # Run multiple times for accuracy
            program_module.sort_numbers(test_data.copy())
        elapsed_time = time.perf_counter() - start_time
        
        # Convert to a score (faster = higher score)
        # Baseline: 1 second = 0.5 score, faster is better
        performance_score = max(0.0, min(1.0, 1.0 - (elapsed_time / 2.0)))
        return performance_score
        
    except Exception:
        return 0.0


if __name__ == "__main__":
    # Test the evaluator with the initial program
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    initial_program_path = os.path.join(script_dir, "initial_program.py")
    
    results = evaluate(initial_program_path)
    print("Evaluation Results:")
    for metric, score in results.items():
        print(f"  {metric}: {score:.4f}")
