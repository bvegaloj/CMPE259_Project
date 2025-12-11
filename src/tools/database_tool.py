"""
Database Tool for SJSU Virtual Assistant
Provides semantic search over the SJSU knowledge database
"""

from typing import Any, List, Dict
from src.database.db_manager import DatabaseManager


class DatabaseTool:
    """Tool for querying the SJSU knowledge database"""
    
    def __init__(self, db_manager=None, db_path: str = "./data/chroma_db"):
        """
        Initialize the database tool
        
        Args:
            db_manager: DatabaseManager instance (optional, will create if not provided)
            db_path: Path to ChromaDB storage (used if db_manager not provided)
        """
        if db_manager is not None:
            self.db_manager = db_manager
        else:
            self.db_manager = DatabaseManager(db_path=db_path)
        self.name = "database_query"
        self.description = "Query the SJSU knowledge database for official information"
    
    def execute(self, query: str, n_results: int = 3) -> str:
        """
        Execute database query
        
        Args:
            query: Query string
            n_results: Number of results to return
            
        Returns:
            Formatted string with results
        """
        try:
            # Check if query is asking about a specific course (e.g., "CMPE 270")
            import re
            course_pattern = r'\b([A-Z]{2,4})\s*(\d{3})\b'
            course_match = re.search(course_pattern, query.upper())
            
            # Query the database
            results = self.db_manager.query(query, n_results=n_results)
            
            # If asking about a specific course, verify it's actually in the results
            if course_match:
                course_code = f"{course_match.group(1)} {course_match.group(2)}"
                course_found = False
                
                if isinstance(results, list):
                    for result in results:
                        content = result.get('content', '').upper()
                        # Check if the exact course code appears in the result
                        if course_code in content or course_code.replace(' ', '') in content:
                            course_found = True
                            break
                
                # If the specific course wasn't found, return a clear message
                if not course_found:
                    return f"No information found for {course_code} in the database. This course may not be in our records. Please check the official SJSU catalog at https://catalog.sjsu.edu or contact the {course_match.group(1)} department directly."
            
            # Check if results is a list (SQLite format) or dict (ChromaDB format)
            if isinstance(results, list):
                # SQLite format - list of dicts
                if not results:
                    return "No relevant information found in the database. This course may not be in our records."
                
                formatted_results = []
                for i, result in enumerate(results, 1):
                    content = result.get('content', '')
                    category = result.get('category', 'general')
                    source = result.get('source', 'database')
                    score = result.get('score', 0.0)
                    
                    # Emphasize the first (most relevant) result
                    prefix = ">>> MOST RELEVANT ANSWER >>> " if i == 1 else ""
                    
                    formatted_results.append(
                        f"{prefix}Result {i} [{category}] (relevance: {score:.2f}):\n{content}"
                    )
                
                return "\n\n".join(formatted_results)
            
            else:
                # ChromaDB format - dict with nested lists
                if not results.get('documents') or not results['documents'][0]:
                    return "No relevant information found in the database. This course may not be in our records."
                
                formatted_results = []
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    distance = results['distances'][0][i] if results.get('distances') else None
                
                result_text = f"Result {i+1}:\n"
                result_text += f"Content: {doc}\n"
                
                if metadata:
                    if 'category' in metadata:
                        result_text += f"Category: {metadata['category']}\n"
                    if 'source' in metadata:
                        result_text += f"Source: {metadata['source']}\n"
                
                if distance is not None:
                    result_text += f"Relevance: {1 - distance:.2f}\n"
                
                formatted_results.append(result_text)
            
                return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error querying database: {str(e)}"
    
    def query_by_category(self, query: str, category: str, n_results: int = 3) -> str:
        """
        Query database with category filter
        
        Args:
            query: Search query
            category: Category to filter by
            n_results: Number of results
            
        Returns:
            Formatted results
        """
        try:
            results = self.db_manager.query_with_filter(
                query,
                filter_dict={"category": category},
                n_results=n_results
            )
            
            if not results['documents'] or not results['documents'][0]:
                return f"No information found in category '{category}'."
            
            formatted_results = []
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append(f"Result {i+1}: {doc}")
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Error querying by category: {str(e)}"
    
    def get_categories(self) -> List[str]:
        """
        Get available categories in the database
        
        Returns:
            List of categories
        """
        try:
            stats = self.db_manager.get_collection_stats()
            return stats.get('categories', [])
        except Exception as e:
            print(f"Error getting categories: {str(e)}")
            return []
    
    def search_multiple_queries(self, queries: List[str], n_results: int = 2) -> Dict[str, str]:
        """
        Execute multiple queries and aggregate results
        
        Args:
            queries: List of query strings
            n_results: Results per query
            
        Returns:
            Dict mapping queries to results
        """
        results = {}
        for query in queries:
            results[query] = self.execute(query, n_results=n_results)
        return results
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get information about this tool
        
        Returns:
            Dict with tool metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'capabilities': [
                'Semantic search over SJSU knowledge base',
                'Category-based filtering',
                'Multiple query aggregation',
                'Relevance scoring'
            ],
            'database_stats': self.db_manager.get_collection_stats()
        }

