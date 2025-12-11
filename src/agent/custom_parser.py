"""
Custom Parser for ReAct Agent Responses
Parses LLM outputs to extract thoughts, actions, and observations
"""

import re
from typing import Dict, Optional, Tuple


class CustomParser:
    """Parser for ReAct-style agent responses"""
    
    @staticmethod
    def parse_react_response(response: str) -> Dict[str, Optional[str]]:
        """
        Parse a ReAct-style response into components
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Dict with 'thought', 'action', 'action_input', 'final_answer'
        """
        result = {
            'thought': None,
            'action': None,
            'action_input': None,
            'final_answer': None
        }
        
        # Check for Final Answer first
        final_answer = CustomParser._extract_final_answer(response)
        if final_answer:
            result['final_answer'] = final_answer
            return result
        
        # Extract Thought
        thought = CustomParser._extract_thought(response)
        if thought:
            result['thought'] = thought
        
        # Extract Action
        action = CustomParser._extract_action(response)
        if action:
            result['action'] = action
        
        # Extract Action Input
        action_input = CustomParser._extract_action_input(response)
        if action_input:
            result['action_input'] = action_input
        
        return result
    
    @staticmethod
    def _extract_thought(response: str) -> Optional[str]:
        """Extract the thought/reasoning from response"""
        # Look for "Thought:" pattern
        match = re.search(r'Thought:\s*(.+?)(?=\n(?:Action:|Final Answer:)|$)', 
                         response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no explicit "Thought:" label, try to extract reasoning
        # Look for text before "Action:" or "Final Answer:"
        match = re.search(r'^(.+?)(?=\n(?:Action:|Final Answer:))', 
                         response, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Only return if it looks like reasoning (not too short)
            if len(text.split()) > 3:
                return text
        
        return None
    
    @staticmethod
    def _extract_action(response: str) -> Optional[str]:
        """Extract the action from response"""
        # Look for "Action:" pattern
        match = re.search(r'Action:\s*(\w+)', response, re.IGNORECASE)
        if match:
            action = match.group(1).strip()
            # Normalize common action names
            action_map = {
                'web_search': 'web_search',
                'websearch': 'web_search',
                'search': 'web_search',
                'database_query': 'database_query',
                'databasequery': 'database_query',
                'database': 'database_query',
                'query': 'database_query'
            }
            return action_map.get(action.lower(), action)
        
        return None
    
    @staticmethod
    def _extract_action_input(response: str) -> Optional[str]:
        """Extract the action input from response"""
        # Look for "Action Input:" pattern
        match = re.search(r'Action Input:\s*(.+?)(?=\n(?:Observation:|Thought:|Action:|Final Answer:)|$)', 
                         response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def _extract_final_answer(response: str) -> Optional[str]:
        """Extract the final answer from response"""
        # Look for "Final Answer:" pattern
        match = re.search(r'Final Answer:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_observation(response: str) -> Optional[str]:
        """Extract observation from response (if present)"""
        # Look for "Observation:" pattern
        match = re.search(r'Observation:\s*(.+?)(?=\n(?:Thought:|Action:|Final Answer:)|$)', 
                         response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def is_final_answer(response: str) -> bool:
        """Check if response contains a final answer"""
        return 'final answer:' in response.lower()
    
    @staticmethod
    def extract_tool_name_and_input(response: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract tool name and input from response
        
        Returns:
            Tuple of (tool_name, tool_input)
        """
        parsed = CustomParser.parse_react_response(response)
        return parsed.get('action'), parsed.get('action_input')
    
    @staticmethod
    def clean_response(response: str) -> str:
        """
        Clean and normalize response text
        
        Args:
            response: Raw response text
            
        Returns:
            Cleaned response text
        """
        # Remove extra whitespace
        response = re.sub(r'\s+', ' ', response)
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Remove any markdown code blocks
        response = re.sub(r'```[\w]*\n?', '', response)
        
        return response
    
    @staticmethod
    def format_agent_step(thought: str, action: str, action_input: str, observation: str) -> str:
        """
        Format an agent reasoning step into a readable string
        
        Args:
            thought: The reasoning/thought
            action: The action taken
            action_input: Input to the action
            observation: Result of the action
            
        Returns:
            Formatted step string
        """
        step = []
        
        if thought:
            step.append(f"Thought: {thought}")
        
        if action:
            step.append(f"Action: {action}")
        
        if action_input:
            step.append(f"Action Input: {action_input}")
        
        if observation:
            step.append(f"Observation: {observation}")
        
        return "\n".join(step)
    
    @staticmethod
    def validate_react_format(response: str) -> Tuple[bool, str]:
        """
        Validate if response follows ReAct format
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for Final Answer
        if CustomParser.is_final_answer(response):
            final_answer = CustomParser._extract_final_answer(response)
            if final_answer and len(final_answer.strip()) > 0:
                return True, "Valid final answer"
            else:
                return False, "Final answer is empty"
        
        # Check for Action
        action = CustomParser._extract_action(response)
        if not action:
            return False, "No action found in response"
        
        # Check for Action Input
        action_input = CustomParser._extract_action_input(response)
        if not action_input:
            return False, "No action input found in response"
        
        return True, "Valid ReAct format"
