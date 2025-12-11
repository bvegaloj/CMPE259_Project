"""
Quick test of evaluation framework with 3 queries
"""

from evaluation.evaluator import Evaluator
from src.utils.logger import logger


def main():
 """Test evaluation with limited queries"""

 logger.info("EVALUATION FRAMEWORK - QUICK TEST")
 logger.info("\nTesting with first 3 queries from each model\n")

 evaluator = Evaluator()

 # Run with limited queries for quick test
 evaluator.run_full_evaluation(max_queries=3)

 logger.info("\n Quick test complete!")
 logger.info("To run full evaluation (20 queries), use:")
 logger.info(" PYTHONPATH=\"$PWD\" .venv/bin/python evaluation/evaluator.py")


if __name__ == "__main__":
 main()
