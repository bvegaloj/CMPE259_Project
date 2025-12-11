#!/usr/bin/env python3
"""
Simple Speed Test - Groq Llama-3.3-70B Performance
Tests raw LLM response speed without complex agent logic
"""

import time
import os
from langchain_groq import ChatGroq

def test_groq_speed():
    """Test Groq API response speed with 5 simple queries"""

    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY not set")
        return

    # Initialize Groq model
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=500
    )

    # Test queries
    queries = [
    "What undergraduate programs are available at SJSU?",
    "What are the admission requirements for Computer Science graduate program?",
    "When does course registration open for Fall 2025?",
    "How do I transfer credits from another university?",
    "What scholarships are available for international students?"
    ]

    print("GROQ LLAMA-3.3-70B SPEED TEST")

    times = []

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/5] Query: {query[:60]}...")

        start = time.time()
        try:
            response = llm.invoke(query)
            elapsed = time.time() - start
            times.append(elapsed)
            response_text = response.content if hasattr(response, 'content') else str(response)
            print(f" Response time: {elapsed:.2f}s")
            print(f" Response: {response_text[:150]}...")

        except Exception as e:
            elapsed = time.time() - start
            print(f" Error after {elapsed:.2f}s: {e}")

    # Summary
    if times:
        print("SUMMARY")
        print(f"Queries processed: {len(times)}/5")
        print(f"Average response time: {sum(times)/len(times):.2f}s")
        print(f"Fastest: {min(times):.2f}s")
        print(f"Slowest: {max(times):.2f}s")
        print(f"Total time: {sum(times):.2f}s")

if __name__ == "__main__":
    test_groq_speed()
