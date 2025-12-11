"""
Custom Evaluation Script for SJSU Virtual Assistant
Using user-specified queries
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.agent_orchestrator import SJSUAgent
from evaluation.metrics import EvaluationMetrics
from src.utils.logger import logger


class CustomEvaluator:
    """Evaluate models with custom queries"""

    def __init__(self, queries_file: str = "../data/queries/test_queries_custom.json"):
        """Initialize evaluator with custom queries"""
        self.queries_file = queries_file
        self.metrics = EvaluationMetrics()

        # Load queries
        with open(queries_file, 'r') as f:
            self.test_queries = json.load(f)

        logger.info(f"Loaded {len(self.test_queries)} custom queries")

        # Create results directory
        self.results_dir = Path("evaluation/results")
        self.results_dir.mkdir(exist_ok=True)

    def evaluate_model(self, model_type: str, max_queries: int = None) -> list:
        """Evaluate a single model on all queries"""
        logger.info(f"EVALUATING {model_type.upper()} MODEL")

        # Initialize agent
        logger.info(f"Initializing {model_type} agent...")
        agent = SJSUAgent(model_type=model_type, verbose=False)
        logger.info("Agent ready\n")

        results = []
        queries = self.test_queries[:max_queries] if max_queries else self.test_queries

        for i, query_data in enumerate(queries, 1):
            logger.info(f"Query {i}/{len(queries)} (ID: {query_data['id']})")
            logger.info(f"Category: {query_data['category']}")
            logger.info(f"Complexity: {query_data['complexity']}")
            logger.info(f"Query: {query_data['query']}")
            logger.info("")

            # Run query
            start_time = time.time()
            response = agent.query(query_data['query'])
            end_time = time.time()
            response_time = end_time - start_time

            # Evaluate
            evaluation = self.metrics.evaluate_single_query(
                query_data=query_data,
                response=response['answer'],
                response_time=response_time,
                model=model_type
            )

            # Log results
            logger.info(f"⏱Response time: {evaluation['metrics']['response_time']:.2f}s")
            logger.info(f"Response preview: {response['answer'][:150]}...")
            logger.info(f"Completeness: {evaluation['metrics']['completeness_score']:.2f}")
            logger.info(f"Relevance: {evaluation['metrics']['relevance_score']:.2f}")

            # Store result
            results.append(evaluation)

        # Calculate summary statistics
        logger.info(f"RESULTS SUMMARY FOR {model_type.upper()}")

        summary = self.metrics.aggregate_results(results)
        logger.info(f"Total queries: {len(results)}")
        logger.info(f"Avg response time: {summary['averages']['response_time']:.2f}s")
        logger.info(f"Avg completeness: {summary['averages']['completeness_score']:.2f}")
        logger.info(f"Avg relevance: {summary['averages']['relevance_score']:.2f}")
        logger.info(f"Avg response length: {summary['averages']['response_length_words']:.0f} words")

        if 'injection_defense_rate' in summary.get('security', {}):
            logger.info(f"Injection defense rate: {summary['security']['injection_defense_rate']:.2f}")

        return results

    def compare_models(self, mistral_results: list, llama_results: list) -> dict:
        """Compare results between two models"""
        # Aggregate by category
        mistral_summary = self.metrics.aggregate_results(mistral_results)
        llama_summary = self.metrics.aggregate_results(llama_results)

        # Determine winners
        winner = {
            "speed": "llama" if llama_summary['averages']['response_time'] < mistral_summary['averages']['response_time'] else "mistral",
            "completeness": "llama" if llama_summary['averages']['completeness_score'] > mistral_summary['averages']['completeness_score'] else "mistral",
            "relevance": "llama" if llama_summary['averages']['relevance_score'] > mistral_summary['averages']['relevance_score'] else "mistral"
        }

        # Detailed query-by-query comparison
        detailed_comparison = []
        for m_result, l_result in zip(mistral_results, llama_results):
            detailed_comparison.append({
                "query_id": m_result['query_id'],
                "query": m_result['query'],
                "mistral": {
                    "time": m_result['metrics']['response_time'],
                    "completeness": m_result['metrics']['completeness_score'],
                    "relevance": m_result['metrics']['relevance_score']
                },
                "llama": {
                    "time": l_result['metrics']['response_time'],
                    "completeness": l_result['metrics']['completeness_score'],
                    "relevance": l_result['metrics']['relevance_score']
                }
            })

        comparison = {
            "mistral": mistral_summary,
            "llama": llama_summary,
            "winner": winner,
            "detailed_comparison": detailed_comparison
        }

        return comparison

    def save_results(self, results: list, model_type: str):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"{model_type}_results_custom_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {filename}")
        return filename

    def save_comparison(self, comparison: dict):
        """Save comparison to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"comparison_custom_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(comparison, f, indent=2)

        logger.info(f"Comparison saved to {filename}")
        return filename

    def run_full_evaluation(self):
        """Run complete evaluation on both models"""
        logger.info("STARTING CUSTOM EVALUATION")
        logger.info(f"Total queries: {len(self.test_queries)}")
        logger.info(f"Estimated time: {len(self.test_queries) * 2 * 45 / 60:.0f}-{len(self.test_queries) * 2 * 90 / 60:.0f} minutes")
        logger.info("")

        # Evaluate Mistral
        mistral_results = self.evaluate_model("mistral")
        self.save_results(mistral_results, "mistral")

        # Evaluate Llama
        llama_results = self.evaluate_model("llama")
        self.save_results(llama_results, "llama")

        # Compare results
        logger.info("FINAL COMPARISON")

        comparison = self.compare_models(mistral_results, llama_results)
        self.save_comparison(comparison)

        # Print comparison summary
        logger.info("PERFORMANCE COMPARISON:")
        logger.info(f"Speed winner: {comparison['winner']['speed'].upper()}")
        logger.info(f"Mistral: {comparison['mistral']['averages']['response_time']:.2f}s")
        logger.info(f"Llama: {comparison['llama']['averages']['response_time']:.2f}s")
        logger.info("")
        logger.info(f"Completeness winner: {comparison['winner']['completeness'].upper()}")
        logger.info(f"Mistral: {comparison['mistral']['averages']['completeness_score']:.2f}")
        logger.info(f"Llama: {comparison['llama']['averages']['completeness_score']:.2f}")
        logger.info("")
        logger.info(f"Relevance winner: {comparison['winner']['relevance'].upper()}")
        logger.info(f"Mistral: {comparison['mistral']['averages']['relevance_score']:.2f}")
        logger.info(f"Llama: {comparison['llama']['averages']['relevance_score']:.2f}")
        logger.info("")

        logger.info("EVALUATION COMPLETE")
        logger.info(f"\nResults saved to: {self.results_dir}")


def main():
    evaluator = CustomEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()
