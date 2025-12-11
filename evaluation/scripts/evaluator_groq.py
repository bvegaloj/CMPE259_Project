#!/usr/bin/env python3
"""
Evaluation with Groq API - Compare Llama-3.3-70B (Groq) vs Mistral-7B (Local)
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agent.agent_orchestrator import SJSUAgent
from evaluation.metrics import EvaluationMetrics

def load_test_queries(file_path: str = "../data/queries/test_queries_custom.json"):
    """Load test queries from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
        # Handle both formats: list or dict with 'queries' key
        if isinstance(data, list):
            return data
        else:
            return data['queries']

def evaluate_model(model_type: str, use_groq: bool = False, queries: list = None) -> Dict[str, Any]:
    """
    Evaluate a model on test queries

    Args:
        model_type: "llama" or "mistral"
        use_groq: Whether to use Groq API (only for llama)
        queries: List of test queries

    Returns:
        Evaluation results
    """
    model_label = f"{model_type}-groq" if use_groq else model_type
    print(f"\n{'='*60}")
    print(f"Evaluating: {model_label.upper()}")
    print(f"{'='*60}\n")

    # Initialize agent
    try:
        agent = SJSUAgent(
            model_type=model_type,
            use_groq=use_groq,
            verbose=False
        )
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return None

    results = []
    total_queries = len(queries)

    for idx, query_data in enumerate(queries, 1):
        query = query_data['query']
        print(f"\n[{idx}/{total_queries}] Query: {query[:80]}...")

        # Run query
        start_time = time.time()
        try:
            result = agent.query(query)
            response = result.get('answer', '')
            elapsed = time.time() - start_time

            # Evaluate response
            eval_result = EvaluationMetrics.evaluate_single_query(
                query_data=query_data,
                response=response,
                response_time=elapsed,
                model=model_label
            )

            results.append(eval_result)

            # Print summary
            print(f"Time: {elapsed:.2f}s")
            print(f"Completeness: {eval_result['metrics']['completeness_score']:.2f}")
            print(f"Response: {response[:100]}...")

        except Exception as e:
            print(f"Error: {str(e)[:100]}")
            # Record timeout/error
            elapsed = time.time() - start_time
            eval_result = {
                "query_id": query_data['id'],
                "query": query,
                "category": query_data.get('category', 'unknown'),
                "model": model_label,
                "response": f"Error: {str(e)}",
                "metrics": {
                    "response_time": elapsed,
                    "completeness_score": 0.0,
                    "relevance_score": 0.0,
                    "length": {"characters": 0, "words": 0, "sentences": 0}
                },
                "completeness_details": {
                    "score": 0.0,
                    "found": [],
                    "missing": query_data.get('expected_info', []),
                    "total_expected": len(query_data.get('expected_info', []))
                },
                "timestamp": datetime.now().isoformat()
            }
            results.append(eval_result)    # Calculate summary statistics
    summary = EvaluationMetrics.aggregate_results(results)

    print(f"SUMMARY - {model_label.upper()}")
    print(f"Total Queries: {len(results)}")
    print(f"Avg Response Time: {summary['averages']['response_time']:.2f}s")
    print(f"Avg Completeness: {summary['averages']['completeness_score']:.2f}")
    print(f"Avg Relevance: {summary['averages']['relevance_score']:.2f}")

    # Count timeouts (completeness = 0)
    timeouts = sum(1 for r in results if r['metrics']['completeness_score'] == 0.0)
    print(f"Timeouts/Errors: {timeouts}/{len(results)} ({timeouts/len(results)*100:.1f}%)")

    return {
        "model": model_label,
        "results": results,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

def compare_results(llama_results: Dict, mistral_results: Dict):
    """Print comparison between models"""
    print("HEAD-TO-HEAD COMPARISON")

    llama_sum = llama_results['summary']['averages']
    mistral_sum = mistral_results['summary']['averages']

    print(f"{'Metric':<25} {'Llama-3.3-70B (Groq)':<20} {'Mistral-7B (Local)':<20} {'Winner'}")

    # Response Time
    llama_time = llama_sum['response_time']
    mistral_time = mistral_sum['response_time']
    time_winner = "Llama" if llama_time < mistral_time else "Mistral"
    print(f"{'Avg Response Time':<25} {llama_time:>10.2f}s {mistral_time:>10.2f}s {time_winner}")

    # Completeness
    llama_comp = llama_sum['completeness_score']
    mistral_comp = mistral_sum['completeness_score']
    comp_winner = "Llama" if llama_comp > mistral_comp else "Mistral"
    print(f"{'Avg Completeness':<25} {llama_comp:>10.2f} {mistral_comp:>10.2f} {comp_winner}")

    # Relevance
    llama_rel = llama_sum['relevance_score']
    mistral_rel = mistral_sum['relevance_score']
    rel_winner = "Llama" if llama_rel > mistral_rel else "Mistral"
    print(f"{'Avg Relevance':<25} {llama_rel:>10.2f} {mistral_rel:>10.2f} {rel_winner}")

    # Timeout rate
    llama_timeouts = sum(1 for r in llama_results['results'] if r['metrics']['completeness_score'] == 0.0)
    mistral_timeouts = sum(1 for r in mistral_results['results'] if r['metrics']['completeness_score'] == 0.0)
    total = len(llama_results['results'])

    llama_timeout_rate = llama_timeouts / total * 100
    mistral_timeout_rate = mistral_timeouts / total * 100
    timeout_winner = "Llama" if llama_timeout_rate < mistral_timeout_rate else "Mistral"
    print(f"{'Timeout Rate':<25} {llama_timeout_rate:>10.1f}% {mistral_timeout_rate:>10.1f}% {timeout_winner}")

    # Overall winner
    llama_wins = sum([
    llama_time < mistral_time,
    llama_comp > mistral_comp,
    llama_rel > mistral_rel,
    llama_timeout_rate < mistral_timeout_rate
    ])

    if llama_wins >= 3:
        print("OVERALL WINNER: Llama-3.3-70B (Groq)")
    else:
        print("OVERALL WINNER: Mistral-7B (Local)")

def main():
    """Run evaluation"""
    print("GROQ API EVALUATION - Llama-3.3-70B vs Mistral-7B")

    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("\nGROQ_API_KEY not set!")
        print("Set it with: export GROQ_API_KEY='your_key_here'")
        return

    # Load queries
    queries = load_test_queries()
    print(f"\nLoaded {len(queries)} test queries")

    # Evaluate Mistral (local) first
    print("Evaluating Mistral-7B (Local Ollama)")
    mistral_results = evaluate_model("mistral", use_groq=False, queries=queries)

    # Save intermediate results
    with open("../data/results/groq_eval_mistral.json", "w") as f:
        json.dump(mistral_results, f, indent=2)
    print(f"\n Mistral results saved to ../data/results/groq_eval_mistral.json")

    # Evaluate Llama (Groq)
    print("Evaluating Llama-3.3-70B (Groq API)")
    llama_results = evaluate_model("llama", use_groq=True, queries=queries)

    # Save results
    with open("../data/results/groq_eval_llama.json", "w") as f:
        json.dump(llama_results, f, indent=2)
    print(f"\n Llama results saved to ../data/results/groq_eval_llama.json")

    # Compare results
    if mistral_results and llama_results:
        compare_results(llama_results, mistral_results)

        # Save combined results
        combined = {
            "evaluation_type": "groq_comparison",
            "timestamp": datetime.now().isoformat(),
            "models": {
                "llama-3.3-70b-groq": llama_results,
                "mistral-7b-local": mistral_results
            }
        }

        with open("../data/results/groq_eval_combined.json", "w") as f:
            json.dump(combined, f, indent=2)

        print("\Combined results saved to ../data/results/groq_eval_combined.json")
        print("\nEvaluation complete!")
    else:
        print("\nEvaluation failed")

if __name__ == "__main__":
    main()
