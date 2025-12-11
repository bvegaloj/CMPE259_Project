#!/usr/bin/env python3
"""
Demo script showing how to use the database and web search tools
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.database_tool import DatabaseTool
from src.tools.web_search_tool import WebSearchTool
from src.utils.logger import logger


def print_section(title):
 """Print a section header"""
 print(f"\n{title}\n")


def demo_database_tool():
 """Demonstrate database tool capabilities"""
 print_section("DATABASE TOOL DEMO")

 db_tool = DatabaseTool('./data/sjsu_database.db')

 # 1. Search programs
 print(" SEARCHING FOR GRADUATE PROGRAMS:")
 result = db_tool.search_programs(degree_type="MS")
 print(result)

 # 2. Get admission requirements
 print("\n\n ADMISSION REQUIREMENTS FOR COMPUTER SCIENCE:")
 result = db_tool.get_admission_requirements("Computer Science")
 print(result)

 # 3. Get prerequisites
 print("\n\n PREREQUISITES FOR CMPE 259:")
 result = db_tool.get_prerequisites("CMPE 259")
 print(result)

 # 4. Get deadlines
 print("\n\n FALL 2025 DEADLINES:")
 result = db_tool.get_deadlines(semester="Fall 2025")
 print(result)

 # 5. Search resources
 print("\n\n CAMPUS RESOURCES (ADVISING):")
 result = db_tool.search_resources(category="Advising")
 print(result)

 # 6. Search FAQs
 print("\n\n FAQS ABOUT SCHOLARSHIPS:")
 result = db_tool.search_faqs("scholarship")
 print(result)

 # 7. Get student clubs
 print("\n\n ACADEMIC CLUBS:")
 result = db_tool.get_student_clubs(category="Academic")
 print(result)


def demo_web_search_tool():
 """Demonstrate web search tool capabilities"""
 print_section("WEB SEARCH TOOL DEMO")

 web_tool = WebSearchTool(max_results=3)

 # 1. General SJSU search
 print(" SEARCHING WEB FOR 'SJSU COMPUTER SCIENCE':")
 result = web_tool.search("SJSU computer science programs")
 print(result)

 # 2. SJSU site-specific search
 print("\n\n SEARCHING SJSU.EDU FOR 'ADMISSIONS':")
 result = web_tool.search_sjsu_site("admissions requirements")
 print(result)

 # 3. Current information
 print("\n\n CURRENT INFORMATION ABOUT SJSU TUITION:")
 result = web_tool.get_current_information("SJSU tuition fees")
 print(result)

 # 4. News search
 print("\n\n RECENT SJSU NEWS:")
 result = web_tool.search_news("SJSU")
 print(result)


def demo_combined_query():
 """Demonstrate how tools complement each other"""
 print_section("COMBINED QUERY DEMO")

 db_tool = DatabaseTool('./data/sjsu_database.db')
 web_tool = WebSearchTool(max_results=2)

 query = "What are the admission requirements for Computer Science?"

 print(f"USER QUERY: {query}\n")

 print("1. CHECKING DATABASE (Static Information):")
 db_result = db_tool.get_admission_requirements("Computer Science")
 print(db_result)

 print("\n\n2. CHECKING WEB (Current Information):")
 web_result = web_tool.search_sjsu_site("Computer Science admission requirements 2025")
 print(web_result)

 print("\n\nINSIGHT: INSIGHT:")
 print("The DATABASE provides structured, reliable baseline requirements.")
 print("The WEB SEARCH provides current updates, deadlines, and application details.")
 print("Together, they provide a complete answer!")


def main():
 """Run all demos"""
 print("\n SJSU VIRTUAL ASSISTANT - TOOLS DEMO")

 try:
    # Demo database tool
    demo_database_tool()

    # Demo web search tool
    demo_web_search_tool()

    # Demo combined usage
    demo_combined_query()

    print("\n DEMO COMPLETE\n")

 except KeyboardInterrupt:
    print("\n\nWarning: Demo interrupted by user")
 except Exception as e:
    print(f"\n\n Error during demo: {e}")
    logger.error(f"Demo error: {e}", exc_info=True)

if __name__ == "__main__":
 main()
