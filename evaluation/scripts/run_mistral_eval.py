#!/usr/bin/env python3
"""
Re-evaluate Mistral-7B with working web search
"""

import json
import time
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agent.agent_orchestrator import AgentOrchestrator
from src.llm.ollama_model import OllamaClient
from src.database.db_manager import DatabaseManager


def load_test_queries():
    """Load test queries"""
    query_file = os.path.join(os.path.dirname(__file__), '../data/queries/test_queries.json')
    with open(query_file, 'r') as f:
        data = json.load(f)
        return data.get('test_queries', data.get('queries', data))


def evaluate_mistral():
    """Run Mistral evaluation"""
    print("MISTRAL-7B RE-EVALUATION")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize components
    print("Initializing Ollama Mistral client and agent")
    llm_client = OllamaClient(model_name="mistral:latest")
    db_manager = DatabaseManager()
    agent = AgentOrchestrator(
        llm_client=llm_client,
        db_manager=db_manager,
        max_iterations=10
    )
    
    # Load queries
    queries = load_test_queries()
    print(f"Loaded {len(queries)} test queries\n")
    
    results = {
        'model': 'Mistral-7B (Ollama)',
        'timestamp': datetime.now().isoformat(),
        'queries': [],
        'statistics': {}
    }
    
    total_time = 0
    successful = 0
    timeouts = 0
    
    for i, query_data in enumerate(queries, 1):
        query = query_data['query']
        print(f"\n[{i}/{len(queries)}] {query}")
        
        start_time = time.time()
        try:
            response = agent.run(query)
            response_time = time.time() - start_time
            
            answer = response.get('response', response.get('answer', str(response)))
            
            # Check for success indicators
            is_timeout = response_time > 120
            has_error = 'error' in answer.lower() or 'OUTPUT_PARSING_FAILURE' in answer
            hit_limit = 'Agent stopped' in answer or 'max iterations' in answer.lower()
            
            success = not is_timeout and not has_error and not hit_limit
            
            if is_timeout:
                timeouts += 1
            if success:
                successful += 1
            
            result = {
                'id': query_data.get('id', i),
                'query': query,
                'category': query_data.get('category', 'unknown'),
                'response': answer[:500] + '...' if len(answer) > 500 else answer,
                'response_time': round(response_time, 2),
                'success': success,
                'timeout': is_timeout,
                'error': has_error,
                'hit_limit': hit_limit
            }
            
            status = "SUCCESS" if success else ("TIMEOUT" if is_timeout else "FAILED")
            print(f"Status: {status} | Time: {response_time:.2f}s")
            print(f"Answer preview: {answer[:150]}...")
            
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                'id': query_data.get('id', i),
                'query': query,
                'category': query_data.get('category', 'unknown'),
                'response': f"Error: {str(e)}",
                'response_time': round(response_time, 2),
                'success': False,
                'timeout': response_time > 120,
                'error': True,
                'hit_limit': False
            }
            print(f"ERROR: {str(e)[:100]}")
        
        results['queries'].append(result)
        total_time += response_time
        
        # Brief pause between queries
        time.sleep(2)
    
    # Calculate statistics
    total_queries = len(queries)
    avg_time = total_time / total_queries if total_queries > 0 else 0
    success_rate = successful / total_queries if total_queries > 0 else 0
    timeout_rate = timeouts / total_queries if total_queries > 0 else 0
    
    results['statistics'] = {
        'total_queries': total_queries,
        'successful': successful,
        'success_rate': round(success_rate * 100, 1),
        'timeouts': timeouts,
        'timeout_rate': round(timeout_rate * 100, 1),
        'avg_response_time': round(avg_time, 2),
        'total_time': round(total_time, 2)
    }
    
    # Save results
    output_file = os.path.join(os.path.dirname(__file__), '../data/results/mistral_reeval.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("EVALUATION SUMMARY")
    print(f"Model: Mistral-7B (Ollama)")
    print(f"Total Queries: {total_queries}")
    print(f"Successful: {successful}/{total_queries} ({success_rate*100:.1f}%)")
    print(f"Timeouts: {timeouts}/{total_queries} ({timeout_rate*100:.1f}%)")
    print(f"Average Response Time: {avg_time:.2f}s")
    print(f"Total Evaluation Time: {total_time/60:.1f} minutes")
    print(f"\nResults saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    evaluate_mistral()
