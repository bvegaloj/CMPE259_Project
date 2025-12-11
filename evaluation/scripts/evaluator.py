"""
Evaluation framework for SJSU Virtual Assistant
Runs comprehensive evaluation on both Llama and Mistral models
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from src.agent.agent_orchestrator import SJSUAgent
from src.utils.logger import logger
from evaluation.metrics import EvaluationMetrics


class Evaluator:
    """Evaluation framework for comparing LLM models"""

    def __init__(self, test_queries_path: str = "../data/queries/test_queries.json"):
        """
        Initialize evaluator

        Args:
            test_queries_path: Path to test queries JSON file
        """
        self.test_queries_path = test_queries_path
        self.test_queries = self._load_test_queries()
        self.results_dir = Path("evaluation/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✓ Loaded {len(self.test_queries)} test queries")

    def _load_test_queries(self) -> List[Dict[str, Any]]:
        """Load test queries from JSON file"""
        try:
            with open(self.test_queries_path, 'r') as f:
                data = json.load(f)
            return data['test_queries']
        except Exception as e:
            logger.error(f"Failed to load test queries: {e}")
            return []

    def evaluate_model(
        self,
        model_type: str,
        model_name: str = None,
        max_queries: int = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a single model on all test queries

        Args:
            model_type: "llama" or "mistral"
            model_name: Specific model name (optional)
            max_queries: Limit number of queries for testing (optional)

        Returns:
            List of evaluation results
        """
        logger.info(f"EVALUATING {model_type.upper()} MODEL")

        # Initialize agent
        logger.info(f"Initializing {model_type} agent...")
        agent = SJSUAgent(model_type=model_type, model_name=model_name, verbose=False)
        logger.info("Agent ready\n")

        results = []
        queries_to_run = self.test_queries[:max_queries] if max_queries else self.test_queries

        for i, query_data in enumerate(queries_to_run, 1):
            logger.info(f"Query {i}/{len(queries_to_run)} (ID: {query_data['id']})")
            logger.info(f"Category: {query_data['category']}")
            logger.info(f"Complexity: {query_data['complexity']}")
            logger.info(f"Query: {query_data['query']}")
            logger.info("")

            try:
                # Time the query
                start_time = time.time()
                response_data = agent.query(query_data['query'])
                end_time = time.time()

                response = response_data['answer']
                response_time = end_time - start_time

                logger.info(f"Response time: {response_time:.2f}s")
                logger.info(f"Response preview: {response[:150]}...")

                # Evaluate the response
                evaluation = EvaluationMetrics.evaluate_single_query(
                    query_data=query_data,
                    response=response,
                    response_time=response_time,
                    model=model_type
                )

                results.append(evaluation)

                logger.info(f"Completeness: {evaluation['metrics']['completeness_score']:.2f}")
                logger.info(f"Relevance: {evaluation['metrics']['relevance_score']:.2f}")

            except Exception as e:
                logger.error(f"Query failed: {e}")
                # Record failed query
                results.append({
                    "query_id": query_data['id'],
                    "query": query_data['query'],
                    "category": query_data['category'],
                    "complexity": query_data['complexity'],
                    "model": model_type,
                    "response": f"ERROR: {str(e)}",
                    "metrics": {
                        "response_time": 0,
                        "completeness_score": 0,
                        "relevance_score": 0,
                        "length": {"words": 0, "characters": 0, "sentences": 0},
                        "injection_defense": False
                    },
                    "error": str(e)
                })

        # Aggregate results
        logger.info(f"RESULTS SUMMARY FOR {model_type.upper()}")

        aggregated = EvaluationMetrics.aggregate_results(results)

        logger.info(f"Total queries: {aggregated['total_queries']}")
        logger.info(f"Avg response time: {aggregated['averages']['response_time']:.2f}s")
        logger.info(f"Avg completeness: {aggregated['averages']['completeness_score']:.2f}")
        logger.info(f"Avg relevance: {aggregated['averages']['relevance_score']:.2f}")
        logger.info(f"Avg response length: {aggregated['averages']['response_length_words']:.0f} words")
        logger.info(f"Injection defense rate: {aggregated['security']['injection_defense_rate']:.2f}")

        return results

    def compare_models(
        self,
        mistral_results: List[Dict[str, Any]],
        llama_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare results between two models

        Args:
            mistral_results: Mistral evaluation results
            llama_results: Llama evaluation results

        Returns:
            Comparison report
        """
        mistral_agg = EvaluationMetrics.aggregate_results(mistral_results)
        llama_agg = EvaluationMetrics.aggregate_results(llama_results)

        comparison = {
            "mistral": mistral_agg,
            "llama": llama_agg,
            "winner": {},
            "detailed_comparison": []
        }

        # Determine winners for each metric
        if mistral_agg['averages']['response_time'] < llama_agg['averages']['response_time']:
            comparison['winner']['speed'] = 'mistral'
        else:
            comparison['winner']['speed'] = 'llama'

        if mistral_agg['averages']['completeness_score'] > llama_agg['averages']['completeness_score']:
            comparison['winner']['completeness'] = 'mistral'
        else:
            comparison['winner']['completeness'] = 'llama'

        if mistral_agg['averages']['relevance_score'] > llama_agg['averages']['relevance_score']:
            comparison['winner']['relevance'] = 'mistral'
        else:
            comparison['winner']['relevance'] = 'llama'

        # Query-by-query comparison
        for m_result, l_result in zip(mistral_results, llama_results):
            comparison['detailed_comparison'].append({
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

        return comparison

    def save_results(self, results: List[Dict[str, Any]], model_type: str):
        """Save evaluation results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_type}_results_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"✓ Results saved to {filepath}")

    def save_comparison(self, comparison: Dict[str, Any]):
        """Save comparison report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(comparison, f, indent=2)

        logger.info(f"✓ Comparison saved to {filepath}")

    def run_full_evaluation(self, max_queries: int = None):
        """
        Run complete evaluation on both models

        Args:
            max_queries: Limit number of queries (for testing)
        """
        logger.info("SJSU VIRTUAL ASSISTANT - FULL EVALUATION")
        logger.info(f"\nEvaluating both models on {max_queries or len(self.test_queries)} queries")
        logger.info("This may take several minutes...\n")

        # Evaluate Mistral
        mistral_results = self.evaluate_model("mistral", max_queries=max_queries)
        self.save_results(mistral_results, "mistral")

        # Evaluate Llama
        llama_results = self.evaluate_model("llama", max_queries=max_queries)
        self.save_results(llama_results, "llama")

        # Compare results
        logger.info("FINAL COMPARISON")

        comparison = self.compare_models(mistral_results, llama_results)
        self.save_comparison(comparison)

        # Print comparison
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
    """Run evaluation"""
    evaluator = Evaluator()

    # Run full evaluation (or limit for testing with max_queries=5)
    evaluator.run_full_evaluation(max_queries=None)


if __name__ == "__main__":
    main()
