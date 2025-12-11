#!/usr/bin/env python3
"""Test database tool natural language parsing"""

import sys
sys.path.insert(0, '.')

from src.tools.database_tool import DatabaseTool

# Create database tool
db = DatabaseTool()

# Test queries
test_queries = [
 "What undergraduate programs are available at SJSU?",
 "SJSU undergraduate programs",
 "list of undergraduate programs at SJSU",
 "What are the admission requirements for Computer Science?",
 "When does course registration open for Fall 2025?",
 "What scholarships are available for international students?",
]

print("Testing Natural Language Query Parsing")

for query in test_queries:
 print(f"\nQuery: {query}")
 result = db.query(query)
 print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")
