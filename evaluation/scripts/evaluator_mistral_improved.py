#!/usr/bin/env python3
"""
Evaluate Improved Mistral - Test if ReAct formatting improvements help
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def evaluate_mistral_improved() -> Dict[str, Any]:
    """Evaluate improved Mistral model"""

    print(f"Evaluating: Mistral-7B (Improved)")

    # Load queries
    queries = load_test_queries()

    # Initialize agent
    agent = SJSUAgent(model_type="mistral", use_groq=False)

    results = {
        'model': 'Mistral-7B-Improved',
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
        
            # Check for failure indicators
            has_parsing_error = 'OUTPUT_PARSING_FAILURE' in response
            hit_iteration_limit = 'Agent stopped' in response

            result = {
                'query_id': query_data.get('id', i),
                'query': query,
                'category': query_data.get('category', 'unknown'),
                'response': response,
                'response_time': round(response_time, 2),
                'completeness': round(completeness, 2),
                'relevance': round(relevance, 2),
                'success': not hit_iteration_limit,
                'timeout': False,
                'has_parsing_error': has_parsing_error,
                'hit_iteration_limit': hit_iteration_limit
                }

                # Status indicator
            if hit_iteration_limit:
                status = " ITERATION LIMIT"
            elif has_parsing_error:
                status = "Warning: PARSING ERROR"
            else:
                status = ""

            print(f"{status} {response_time:.2f}s | C:{completeness:.2f} | R:{relevance:.2f}")

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
                'error': str(e),
                'has_parsing_error': False,
                'hit_iteration_limit': False
            }
            print(f" ERROR: {str(e)[:60]}")

        results['queries'].append(result)
        time.sleep(1)

        # Calculate statistics
        successful_queries = [r for r in results['queries'] if r['success']]
        parsing_errors = [r for r in results['queries'] if r.get('has_parsing_error', False)]
        iteration_limits = [r for r in results['queries'] if r.get('hit_iteration_limit', False)]

        if successful_queries:
            results['statistics'] = {
                'total_queries': len(queries),
                'successful_queries': len(successful_queries),
                'success_rate': round(len(successful_queries) / len(queries), 2),
                'avg_response_time': round(sum(r['response_time'] for r in successful_queries) / len(successful_queries), 2),
                'avg_completeness': round(sum(r['completeness'] for r in successful_queries) / len(successful_queries), 2),
                'avg_relevance': round(sum(r['relevance'] for r in successful_queries) / len(successful_queries), 2),
                'parsing_errors': len(parsing_errors),
                'iteration_limits': len(iteration_limits),
                'parsing_error_rate': round(len(parsing_errors) / len(queries), 2),
                'iteration_limit_rate': round(len(iteration_limits) / len(queries), 2)
                }
        else:
            results['statistics'] = {
                'total_queries': len(queries),
                'successful_queries': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'avg_completeness': 0.0,
                'avg_relevance': 0.0,
                'parsing_errors': len(parsing_errors),
                'iteration_limits': len(iteration_limits),
                'parsing_error_rate': round(len(parsing_errors) / len(queries), 2),
                'iteration_limit_rate': round(len(iteration_limits) / len(queries), 2)
                }

        return results

def main():
    """Run evaluation"""
    print("MISTRAL IMPROVEMENT EVALUATION")

    results = evaluate_mistral_improved()

    # Save results
    output_file = "evaluation/mistral_improved.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n Results saved to {output_file}")

    # Display summary
    stats = results['statistics']
    print("RESULTS SUMMARY")
    print(f"Success Rate: {stats['success_rate']*100:.1f}%")
    print(f"Avg Response Time: {stats['avg_response_time']:.2f}s")
    print(f"Avg Completeness: {stats['avg_completeness']:.2f}")
    print(f"Avg Relevance: {stats['avg_relevance']:.2f}")
    print(f"Parsing Errors: {stats['parsing_errors']}/{stats['total_queries']} ({stats['parsing_error_rate']*100:.1f}%)")
    print(f"Iteration Limits: {stats['iteration_limits']}/{stats['total_queries']} ({stats['iteration_limit_rate']*100:.1f}%)")

    # Compare to original
    print("COMPARISON TO ORIGINAL MISTRAL")
    print("Original Results:")
    print(" Success Rate: 50.0% (10/20 completed)")
    print(" Parsing Errors: 35.0% (7/20)")
    print(" Iteration Limits: 50.0% (10/20)")
    print(" Avg Completeness: 0.33")
    print(" Avg Relevance: 0.16")
    print("\nImproved Results:")
    print(f" Success Rate: {stats['success_rate']*100:.1f}% ({stats['successful_queries']}/{stats['total_queries']} completed)")
    print(f" Parsing Errors: {stats['parsing_error_rate']*100:.1f}% ({stats['parsing_errors']}/{stats['total_queries']})")
    print(f" Iteration Limits: {stats['iteration_limit_rate']*100:.1f}% ({stats['iteration_limits']}/{stats['total_queries']})")
    print(f" Avg Completeness: {stats['avg_completeness']:.2f}")
    print(f" Avg Relevance: {stats['avg_relevance']:.2f}")

    # Calculate improvements
    if stats['success_rate'] > 0.5:
        improvement = ((stats['success_rate'] - 0.5) / 0.5) * 100
        print(f"\nSuccess rate improved by {improvement:.1f}%!")
    elif stats['success_rate'] < 0.5:
        decline = ((0.5 - stats['success_rate']) / 0.5) * 100
        print(f"\nWarning: Success rate declined by {decline:.1f}%")
    else:
        print(f"\n No change in success rate")

if __name__ == "__main__":
    main()
