#!/usr/bin/env python3
"""
Evaluation - Database-only (no web search to avoid hangs)
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agent.agent_orchestrator import SJSUAgent
from evaluation.metrics import EvaluationMetrics

def load_test_queries(file_path: str = "../data/queries/test_queries_custom.json"):
    """Load test queries from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        else:
            return data['queries']

def evaluate_model(model_type: str, use_groq: bool, queries: list) -> Dict[str, Any]:
    """Evaluate a model"""

    model_name = f"{'Groq-' if use_groq else ''}{'Llama-3.3-70B' if model_type == 'llama' else 'Mistral-7B'}"

    print(f"Evaluating: {model_name}")

    # Initialize agent (disable web search)
    agent = SJSUAgent(model_type=model_type, use_groq=use_groq)

    results = {
        'model': model_name,
        'queries': [],
        'timestamp': datetime.now().isoformat()
    }

    metrics = EvaluationMetrics()

    for i, query_data in enumerate(queries, 1):
        query = query_data['query']
        print(f"\n[{i}/{len(queries)}] {query}...")

        start_time = time.time()
        try:
            response_dict = agent.query(query)
            response_time = time.time() - start_time

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

            print(f"✓ {response_time:.2f}s | C:{completeness:.2f} | R:{relevance:.2f}")

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
            print(f"{str(e)[:60]}")

        results['queries'].append(result)
        time.sleep(1)  # Brief pause

    # Calculate statistics
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
    print("MODEL COMPARISON EVALUATION")
    print("Groq Llama-3.3-70B vs Local Mistral-7B")

    queries = load_test_queries()
    print(f"\nLoaded {len(queries)} test queries\n")

    # Evaluate Groq Llama
    print("Evaluating Groq Llama-3.3-70B")
    llama_results = evaluate_model('llama', use_groq=True, queries=queries)

    with open('../data/results/final_llama_groq.json', 'w') as f:
        json.dump(llama_results, f, indent=2)
    print(f"\n Llama results saved")

    # Evaluate Mistral
    print("Evaluating Local Mistral-7B")
    mistral_results = evaluate_model('mistral', use_groq=False, queries=queries)

    with open('../data/results/final_mistral.json', 'w') as f:
        json.dump(mistral_results, f, indent=2)
    print(f"\n Mistral results saved")

    # Display comparison
    print("FINAL COMPARISON")

    print(f"\n{'Model':<25} {'Success':<12} {'Avg Time':<12} {'Completeness':<15} {'Relevance'}")

    for results in [llama_results, mistral_results]:
        stats = results['statistics']
        print(f"{results['model']:<25} {stats['success_rate']*100:>6.1f}%     {stats['avg_response_time']:>6.2f}s       {stats['avg_completeness']:>6.2f}            {stats['avg_relevance']:>6.2f}")

    print(" Evaluation Complete!")

if __name__ == "__main__":
    main()
