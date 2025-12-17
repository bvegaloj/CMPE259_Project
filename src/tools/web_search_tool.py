"""
Web Search Tool for SJSU Virtual Assistant
Provides web search capabilities using Tavily API
"""

from typing import Any, List, Dict, Optional
import os
from tavily import TavilyClient


class WebSearchTool:
    """Tool for searching the web for SJSU information using Tavily API"""
    
    def __init__(self):
        """Initialize the web search tool"""
        self.name = "web_search"
        self.description = "Search the web for current information about SJSU"
        
        # Initialize Tavily client
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        self.client = TavilyClient(api_key=api_key)
    
    def execute(self, query: str, max_results: int = 3, include_domains: list = None) -> str:
        """
        Execute a web search using Tavily
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            include_domains: Optional list of domains to prioritize (e.g., ['sjsu.edu'])
            
        Returns:
            Formatted search results
        """
        try:
            # Add SJSU context to query if not present
            if "sjsu" not in query.lower() and "san jose state" not in query.lower():
                query = f"SJSU {query}"
            
            # Check if this is a location/building query - prioritize official SJSU sources
            location_terms = ['location', 'address', 'building', 'office', 'where', 'find', 'directions']
            is_location_query = any(term in query.lower() for term in location_terms)
            
            # Build search parameters
            search_params = {
                'query': query,
                'max_results': max_results,
                'search_depth': 'advanced',
                'include_raw_content': False
            }
            
            # For location queries, prioritize SJSU official site and DISABLE AI summary
            # (AI summaries can hallucinate addresses - use only actual page content)
            if is_location_query:
                search_params['include_domains'] = ['sjsu.edu']
                search_params['include_answer'] = False  # Don't trust AI for addresses
                search_params['include_raw_content'] = True  # Get actual page content
            else:
                search_params['include_answer'] = True
                if include_domains:
                    search_params['include_domains'] = include_domains
            
            # Perform search using Tavily
            response = self.client.search(**search_params)
            
            if not response or 'results' not in response:
                return "No search results found."
            
            # Format results with AI answer if available (but not for location queries)
            formatted_results = []
            
            # Add AI-generated answer if available (skipped for location queries)
            if response.get('answer') and not is_location_query:
                formatted_results.append(f"Summary: {response['answer']}\n")
            
            # Add individual results
            results = response['results']
            for i, result in enumerate(results, 1):
                result_text = f"Result {i}:\n"
                result_text += f"Title: {result.get('title', 'N/A')}\n"
                result_text += f"URL: {result.get('url', 'N/A')}\n"
                
                # For location queries, use more content to capture full address
                if is_location_query:
                    # Use raw_content if available, else content - with longer limit for addresses
                    raw = result.get('raw_content') or result.get('content', '')
                    content = raw[:800] + "..." if len(raw) > 800 else raw
                    result_text += f"Content: {content}\n"
                elif result.get('content'):
                    # Truncate content to keep it reasonable
                    content = result['content'][:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', '')
                    result_text += f"Content: {content}\n"
                formatted_results.append(result_text)
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def search_sjsu_site(self, query: str, max_results: int = 3) -> str:
        """
        Search specifically on sjsu.edu domain
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Formatted search results
        """
        site_query = f"site:sjsu.edu {query}"
        return self.execute(site_query, max_results)
    
    def search_multiple_queries(self, queries: List[str], max_results: int = 2) -> Dict[str, str]:
        """
        Execute multiple search queries
        
        Args:
            queries: List of query strings
            max_results: Results per query
            
        Returns:
            Dict mapping queries to results
        """
        results = {}
        for query in queries:
            results[query] = self.execute(query, max_results=max_results)
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
                'Web search via DuckDuckGo',
                'SJSU-specific search',
                'Site-specific search (sjsu.edu)',
                'Multiple query support'
            ],
            'search_engine': 'DuckDuckGo'
        }
