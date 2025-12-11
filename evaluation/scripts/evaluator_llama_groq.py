#!/usr/bin/env python3
"""
Evaluation with Groq API - Llama-3.3-70B Only
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

def evaluate_model(queries: list = None) -> Dict[str, Any]:
    """
    Evaluate Groq-powered Llama model

    Returns:
        Dict with evaluation results
    """
    print("\nEvaluating: LLAMA-3.3-70B (Groq API)\n")

    # Initialize agent with Groq
    agent = SJSUAgent(model_type='llama', use_groq=True)

    results = {
    'model': 'Llama-3.3-70B (Groq)',
    'queries': [],
    'timestamp': datetime.now().isoformat()
    }

    metrics = EvaluationMetrics()

    for i, query_data in enumerate(queries, 1):
        query = query_data['query']
    print(f"\n[{i}/{len(queries)}] Query: {query}...")

    start_time = time.time()
    try:
        response_dict = agent.query(query)
        response_time = time.time() - start_time

        # Extract answer from response dict
        response = response_dict.get('answer', str(response_dict))

        # Calculate metrics
        completeness_result = metrics.check_completeness(
        response,
            query_data.get('expected_info', [])
        )
        completeness = completeness_result['score']
        relevance = metrics.check_relevance(query, response)
        result = {
        'query_id': query_data.get('id', i),
        'query': query,
        'category': query_data.get('category', 'unknown'),
        'response': response,
        'response_time': round(response_time, 2),
        'completeness': round(completeness, 2),
        'relevance': round(relevance, 2),
        'success': True,
        'timeout': False
        }

        print(f" Response time: {response_time:.2f}s | Completeness: {completeness:.2f} | Relevance: {relevance:.2f}")

    except Exception as e:
        response_time = time.time() - start_time
        result = {
        'query_id': query_data.get('id', i),
        'query': query,
        'category': query_data.get('category', 'unknown'),
        'response': f"Error: {str(e)}",
        'response_time': round(response_time, 2),
        'completeness': 0.0,
        'relevance': 0.0,
        'success': False,
        'timeout': response_time > 120,
        'error': str(e)
        }
        print(f" Error: {str(e)}")

    results['queries'].append(result)

    # Brief pause between queries
    time.sleep(1)

    # Calculate overall statistics
    successful_queries = [r for r in results['queries'] if r['success']]

    if successful_queries:
        results['statistics'] = {
    'total_queries': len(queries),
    'successful_queries': len(successful_queries),
    'success_rate': round(len(successful_queries) / len(queries), 2),
    'avg_response_time': round(sum(r['response_time'] for r in successful_queries) / len(successful_queries), 2),
    'avg_completeness': round(sum(r['completeness'] for r in successful_queries) / len(successful_queries), 2),
    'avg_relevance': round(sum(r['relevance'] for r in successful_queries) / len(successful_queries), 2),
    'timeout_rate': round(sum(1 for r in results['queries'] if r.get('timeout', False)) / len(queries), 2)
    }
    else:
        results['statistics'] = {
    'total_queries': len(queries),
    'successful_queries': 0,
    'success_rate': 0.0,
    'avg_response_time': 0.0,
    'avg_completeness': 0.0,
    'avg_relevance': 0.0,
    'timeout_rate': 1.0
    }

    return results

def main():
    print("GROQ API EVALUATION - Llama-3.3-70B Performance Test")

    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("\n GROQ_API_KEY not set!")
        print("Set it with: export GROQ_API_KEY='your_key_here'")
        return

    # Load queries
    queries = load_test_queries()
    print(f"Loaded {len(queries)} test queries\n")

    # Evaluate Groq-powered Llama
    print("="*60)
    print("Evaluating Llama-3.3-70B with Groq API")
    print("="*60)

    llama_results = evaluate_model(queries=queries)

    # Save results
    output_file = 'evaluation/llama_groq_results.json'
    with open(output_file, 'w') as f:
        json.dump(llama_results, f, indent=2)

    print(f"\n Results saved to {output_file}")

    # Display summary
    print("EVALUATION SUMMARY")

    stats = llama_results['statistics']
    print(f"\nLlama-3.3-70B (Groq API):")
    print(f" Success Rate: {stats['success_rate']*100:.1f}%")
    print(f" Avg Response Time: {stats['avg_response_time']:.2f}s")
    print(f" Avg Completeness: {stats['avg_completeness']:.2f}")
    print(f" Avg Relevance: {stats['avg_relevance']:.2f}")
    print(f" Timeout Rate: {stats['timeout_rate']*100:.1f}%")

    print(" Evaluation complete!")

if __name__ == "__main__":
    main()
