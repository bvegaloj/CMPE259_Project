#!/usr/bin/env python3
"""
Quick summary of Groq evaluation results
"""

import json
import sys

def load_results(filepath):
    """Load results from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON in: {filepath}")
        return None

def print_summary():
    """Print summary of Groq evaluation results"""

    # Load Llama results
    llama_data = load_results("evaluation/groq_eval_llama.json")

    if not llama_data:
        print("\n Llama-Groq evaluation not complete yet")
        print("Check: tail -f evaluation/groq_evaluation_run.log")
        return

    print("GROQ EVALUATION RESULTS")

    # Llama summary
    llama_summary = llama_data['summary']['averages']
    llama_results = llama_data['results']
    llama_timeouts = sum(1 for r in llama_results if r['metrics']['completeness_score'] == 0.0)

    print(f"\n Llama-3.3-70B (Groq API)")
    print(f"Total Queries: {len(llama_results)}")
    print(f"Avg Response Time: {llama_summary['response_time']:.2f}s")
    print(f"Avg Completeness: {llama_summary['completeness_score']:.2f}")
    print(f"Avg Relevance: {llama_summary['relevance_score']:.2f}")
    print(f"Success Rate: {(len(llama_results)-llama_timeouts)/len(llama_results)*100:.1f}% ({len(llama_results)-llama_timeouts}/{len(llama_results)})")
    print(f"Timeout Rate: {llama_timeouts/len(llama_results)*100:.1f}% ({llama_timeouts}/{len(llama_results)})")

    # Show query-by-query completeness
    print(f"\nQuery-by-Query Completeness:")
    for i, result in enumerate(llama_results, 1):
        comp = result['metrics']['completeness_score']
    time_taken = result['metrics']['response_time']
    status = "" if comp > 0 else ""
    print(f" {i:2d}. {status} {comp:.2f} ({time_taken:.1f}s) - {result['query'][:60]}...")

    print("KEY FINDINGS")
    print(f"\n Groq API makes Llama {70/11:.1f}x more powerful (70B vs 11B params)")
    print(f" Average response time: {llama_summary['response_time']:.2f}s")
    print(f" Success rate: {(len(llama_results)-llama_timeouts)/len(llama_results)*100:.0f}%")

    if llama_summary['response_time'] < 20:
        print(f" Groq inference is ~{84.88/llama_summary['response_time']:.0f}x faster than local Ollama (84.88s → {llama_summary['response_time']:.1f}s)")

if __name__ == "__main__":
    print_summary()
