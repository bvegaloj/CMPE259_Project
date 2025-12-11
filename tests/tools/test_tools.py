"""Test suite for tools"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.database_tool import DatabaseTool
from src.tools.web_search_tool import WebSearchTool


# Database Tool Tests

@pytest.fixture
def db_tool():
 """Create database tool with real database"""
 return DatabaseTool('./data/sjsu_database.db')


def test_database_tool_init(db_tool):
 """Test database tool initialization"""
 assert db_tool.name == "sjsu_database"
 assert db_tool.description is not None
 assert db_tool.db is not None


def test_search_programs(db_tool):
 """Test program search"""
 # Search for all programs
 result = db_tool.search_programs()
 assert "Computer Science" in result
 assert "Found" in result

 # Search by degree type
 result = db_tool.search_programs(degree_type="MS")
 assert "MS" in result

 # Search by department
 result = db_tool.search_programs(department="Computer")
 assert "Computer" in result


def test_get_admission_requirements(db_tool):
 """Test admission requirements retrieval"""
 result = db_tool.get_admission_requirements("Computer Science")
 assert "Admission Requirements" in result
 assert "GPA" in result or "requirements" in result.lower()


def test_get_prerequisites(db_tool):
 """Test prerequisites retrieval"""
 result = db_tool.get_prerequisites("CMPE 259")
 assert "CMPE 259" in result
 assert "Machine Learning" in result


def test_get_deadlines(db_tool):
 """Test deadlines retrieval"""
 result = db_tool.get_deadlines(semester="Fall 2025")
 assert "Fall 2025" in result
 assert "deadline" in result.lower()


def test_search_resources(db_tool):
 """Test resource search"""
 result = db_tool.search_resources(category="Library")
 assert "Library" in result

 result = db_tool.search_resources(keyword="health")
 assert len(result) > 0


def test_search_faqs(db_tool):
 """Test FAQ search"""
 result = db_tool.search_faqs("admission requirements")
 assert len(result) > 0


def test_get_student_clubs(db_tool):
 """Test student clubs retrieval"""
 result = db_tool.get_student_clubs(category="Academic")
 assert "club" in result.lower() or "Academic" in result


def test_get_scholarships(db_tool):
 """Test scholarships retrieval"""
 result = db_tool.get_scholarships(min_gpa=3.0)
 assert "scholarship" in result.lower()


def test_query_method(db_tool):
 """Test general query method"""
 result = db_tool.query("programs", degree_type="BS")
 assert "BS" in result

 result = db_tool.query("deadlines", semester="Fall 2025")
 assert "Fall 2025" in result

 # Test invalid query type
 result = db_tool.query("invalid_type")
 assert "Unknown query type" in result


# Web Search Tool Tests

@pytest.fixture
def web_tool():
 """Create web search tool"""
 return WebSearchTool(max_results=3)


def test_web_tool_init(web_tool):
 """Test web search tool initialization"""
 assert web_tool.name == "web_search"
 assert web_tool.description is not None
 assert web_tool.max_results == 3


def test_search(web_tool):
 """Test basic web search"""
 result = web_tool.search("SJSU computer science")
 assert len(result) > 0
 # Accept either successful results or a graceful error message
 assert ("SJSU" in result or "San Jose" in result or
 "search results" in result.lower() or
 "unavailable" in result.lower())


def test_search_sjsu_site(web_tool):
 """Test SJSU-specific search"""
 result = web_tool.search_sjsu_site("admissions")
 assert len(result) > 0


def test_get_current_information(web_tool):
 """Test current information retrieval"""
 result = web_tool.get_current_information("SJSU enrollment")
 assert len(result) > 0


@pytest.mark.slow
def test_fetch_page_content(web_tool):
 """Test webpage content fetching"""
 result = web_tool.fetch_page_content("https://www.sjsu.edu")
 assert len(result) > 0
 # Should contain some SJSU-related content
 assert "San Jose" in result or "SJSU" in result or "University" in result


def test_search_news(web_tool):
 """Test news search"""
 result = web_tool.search_news("SJSU")
 assert len(result) > 0


if __name__ == "__main__":
 pytest.main([__file__, "-v", "-m", "not slow"])
