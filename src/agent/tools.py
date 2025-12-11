"""
Tool Definitions for SJSU Virtual Assistant Agent
Defines the tools available to the ReAct agent
"""

from typing import List, Dict, Any
from src.tools.web_search import WebSearchTool
from src.tools.database_query import DatabaseQueryTool


class AgentTools:
    """Manages tools available to the agent"""
    
    def __init__(self):
        """Initialize all available tools"""
        self.tools = {
            'web_search': WebSearchTool(),
            'database_query': DatabaseQueryTool()
        }
    
    def get_tool(self, tool_name: str):
        """
        Get a tool by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def execute_tool(self, tool_name: str, tool_input: str) -> Any:
        """
        Execute a tool with given input
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            return f"Error: Tool '{tool_name}' not found"
        
        try:
            result = tool.execute(tool_input)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """
        Get descriptions of all available tools
        
        Returns:
            List of tool descriptions
        """
        descriptions = []
        
        descriptions.append({
            'name': 'web_search',
            'description': 'Search the web for current information about SJSU. Use this when you need recent or real-time information.',
            'input': 'A search query string'
        })
        
        descriptions.append({
            'name': 'database_query',
            'description': 'Query the SJSU knowledge database for official information about programs, admissions, requirements, etc. Use this for authoritative university information.',
            'input': 'A query about SJSU information'
        })
        
        return descriptions
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def format_tool_descriptions(self) -> str:
        """
        Format tool descriptions for LLM prompt
        
        Returns:
            Formatted string with tool descriptions
        """
        descriptions = self.get_tool_descriptions()
        
        formatted = "Available Tools:\n"
        for i, desc in enumerate(descriptions, 1):
            formatted += f"\n{i}. {desc['name']}\n"
            formatted += f"   Description: {desc['description']}\n"
            formatted += f"   Input: {desc['input']}\n"
        
        return formatted
    
    def validate_tool_name(self, tool_name: str) -> bool:
        """
        Check if a tool name is valid
        
        Args:
            tool_name: Name to validate
            
        Returns:
            True if valid, False otherwise
        """
        return tool_name in self.tools
    
    def get_tool_count(self) -> int:
        """Get the number of available tools"""
        return len(self.tools)


def get_available_tools() -> List[str]:
    """
    Convenience function to get list of available tool names
    
    Returns:
        List of tool names
    """
    tools = AgentTools()
    return tools.get_tool_names()


def get_tool_descriptions_text() -> str:
    """
    Convenience function to get formatted tool descriptions
    
    Returns:
        Formatted tool descriptions
    """
    tools = AgentTools()
    return tools.format_tool_descriptions()
