"""
Agent Orchestrator for SJSU Virtual Assistant
Coordinates the ReAct agent loop with tools and LLM integration
"""

from typing import Dict, List, Any, Optional
import json
import re
from src.tools.web_search_tool import WebSearchTool
from src.tools.database_tool import DatabaseTool


class AgentOrchestrator:
    """Orchestrates the ReAct agent reasoning and action loop"""
    
    def __init__(self, llm_client, db_manager=None, config=None, max_iterations: int = 5):
        """
        Initialize the agent orchestrator
        
        Args:
            llm_client: LLM client instance (MistralClient or GroqClient)
            db_manager: Database manager instance (optional)
            config: Configuration object (optional)
            max_iterations: Maximum reasoning iterations
        """
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.config = config
        
        # Initialize tools
        self.tools = {
            'web_search': WebSearchTool(),
            'database_query': DatabaseTool(db_manager=db_manager)
        }
        
        # Track conversation history
        self.conversation_history = []
    
    def run(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the ReAct agent loop
        
        Args:
            query: User query
            context: Optional additional context
            
        Returns:
            Dict with response, reasoning steps, and metadata
        """
        print(f"\nProcessing query: {query}")
        
        # Initialize tracking
        reasoning_steps = []
        iteration = 0
        final_answer = None
        
        # Build initial prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, context)
        
        while iteration < self.max_iterations and not final_answer:
            iteration += 1
            print(f"\nIteration {iteration}/{self.max_iterations}")
            
            # Get LLM reasoning
            try:
                response = self.llm_client.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    conversation_history=self.conversation_history
                )
                
                print(f"Reasoning: {response[:200]}..." if len(response) > 200 else f"Reasoning: {response}")
                
                # Parse the response
                action, action_input, observation = self._parse_response(response)
                
                step = {
                    'iteration': iteration,
                    'thought': response,
                    'action': action,
                    'action_input': action_input,
                    'observation': observation
                }
                
                reasoning_steps.append(step)
                
                # Check if we have a final answer
                if action == 'Final Answer':
                    final_answer = observation
                    print(f"\nFinal Answer: {final_answer}")
                    break
                
                # Execute the action
                if action in self.tools:
                    try:
                        tool_result = self.tools[action].execute(action_input)
                        observation = tool_result
                        step['observation'] = observation
                        
                        # Print full observation for debugging
                        print(f"\n{'='*80}")
                        print(f"TOOL OBSERVATION FOR LLM:")
                        print(f"{'='*80}")
                        print(observation)
                        print(f"{'='*80}\n")
                        
                        # Print truncated version for console
                        print(f"Observation: {observation[:200]}..." if len(str(observation)) > 200 else f"Observation: {observation}")
                        
                        # AUTO-FALLBACK: If database_query returns "No information found" and it's about a course,
                        # automatically try web_search with Tavily
                        if action == 'database_query' and 'No information found' in observation:
                            print("\n⚠️  Database returned no results - automatically trying web_search with Tavily...")
                            # Extract course code from observation
                            import re
                            course_match = re.search(r'([A-Z]{2,4}\s*\d{3})', observation)
                            if course_match:
                                course_code = course_match.group(1)
                                print(f"   Searching web for {course_code} prerequisites...\n")
                                
                                # Automatically trigger web search with Tavily
                                web_search_query = f"SJSU {course_code} course prerequisites requirements"
                                try:
                                    observation = self.tools['web_search'].execute(web_search_query)
                                    step['action'] = 'web_search'
                                    step['action_input'] = web_search_query
                                    step['observation'] = observation
                                    print(f"✓ Web search completed for {course_code}")
                                except Exception as web_error:
                                    observation = f"Could not find information for {course_code}. Please check the official SJSU catalog: https://catalog.sjsu.edu"
                                    step['observation'] = observation
                                    print(f"Web search failed: {web_error}")
                        
                    except Exception as e:
                        observation = f"Error executing {action}: {str(e)}"
                        step['observation'] = observation
                        print(f"Error: {observation}")
                
                # Update prompt with new observation
                user_prompt = self._update_prompt(user_prompt, step)
                
            except Exception as e:
                print(f"Error in iteration {iteration}: {str(e)}")
                error_step = {
                    'iteration': iteration,
                    'error': str(e)
                }
                reasoning_steps.append(error_step)
                break
        
        # If no final answer, use last response
        if not final_answer and reasoning_steps:
            last_step = reasoning_steps[-1]
            final_answer = last_step.get('observation', last_step.get('thought', 'Unable to generate response'))
        
        
        result = {
            'query': query,
            'response': final_answer or "I apologize, but I couldn't generate a proper response.",
            'reasoning_steps': reasoning_steps,
            'iterations': iteration,
            'metadata': {
                'model': self.llm_client.model_name,
                'max_iterations': self.max_iterations,
                'completed': final_answer is not None
            }
        }
        
        # Update conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': query
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': final_answer or "Unable to respond"
        })
        
        return result
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for ReAct agent"""
        return """You are a helpful SJSU Virtual Assistant that uses the ReAct (Reasoning and Acting) framework to answer student questions.

You have access to the following tools:
- database_query: Query the SJSU knowledge database for official information about courses, prerequisites, programs, deadlines, FAQs, campus resources, etc. ALWAYS use this tool FIRST for any SJSU-specific questions.
- web_search: Search the web for current information not in the database

Use this format:

Thought: Consider what information you need to answer the question
Action: [tool_name]
Action Input: [input for the tool]
Observation: [result from the tool]
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information to answer
Final Answer: [your complete answer to the user]

CRITICAL RULES - READ CAREFULLY:
1. ALWAYS use database_query tool FIRST for questions about SJSU courses, prerequisites, programs, or policies
2. If database_query returns "No information found" or "This course may not be in our records", you MUST use web_search tool next
3. When using web_search, search for "SJSU [course code] prerequisites" to find current information
4. When you see the Observation from database_query with actual course information, read it WORD BY WORD
5. Your Final Answer MUST use the EXACT text from the Observation - DO NOT CHANGE ANY WORDS
6. DO NOT add any information that is not in the Observation
7. DO NOT substitute or add different course codes than what appears in the results
8. The >>> MOST RELEVANT ANSWER >>> marker shows you the best result - use ONLY that information
9. Copy the prerequisite requirements EXACTLY as they appear - including phrases like "or instructor consent"
10. DO NOT hallucinate or invent course numbers that are not in the Observation
11. If BOTH database_query AND web_search fail, then say: "I couldn't find information about this course. Please check https://catalog.sjsu.edu or contact the department."
12. NEVER make up prerequisites - always use tools first"""
    
    def _build_user_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Build the initial user prompt"""
        prompt = f"Question: {query}\n\n"
        if context:
            prompt += f"Additional Context: {context}\n\n"
        prompt += "Begin your reasoning:"
        return prompt
    
    def _update_prompt(self, current_prompt: str, step: Dict[str, Any]) -> str:
        """Update prompt with latest reasoning step"""
        update = f"\n\nThought: {step.get('thought', '')}"
        if step.get('action'):
            update += f"\nAction: {step['action']}"
        if step.get('action_input'):
            update += f"\nAction Input: {step['action_input']}"
        if step.get('observation'):
            update += f"\nObservation: {step['observation']}"
        update += "\n\nContinue reasoning:"
        return current_prompt + update
    
    def _parse_response(self, response: str) -> tuple:
        """
        Parse LLM response to extract action and input
        
        Returns:
            Tuple of (action, action_input, observation)
        """
        # Parse Action and Action Input FIRST (before checking for Final Answer)
        # This prevents the LLM from hallucinating observations and jumping to Final Answer
        action = None
        action_input = None
        
        # Look for Action
        action_match = re.search(r'Action:\s*(\w+)', response, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip()
        
        # Look for Action Input
        input_match = re.search(r'Action Input:\s*(.+?)(?:\n(?:Observation|Thought|Final Answer)|\Z)', response, re.IGNORECASE | re.DOTALL)
        if input_match:
            action_input = input_match.group(1).strip()
        
        # If we found an action, return it (ignore any Final Answer that comes after)
        if action and action_input:
            return action, action_input, None
        
        # Only check for Final Answer if no action was found
        if 'Final Answer:' in response or 'final answer:' in response.lower():
            # Extract everything after "Final Answer:"
            match = re.search(r'Final Answer:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
            if match:
                return 'Final Answer', None, match.group(1).strip()
        
        # If we found an action but no input, use a default search
        if action and not action_input:
            action_input = "SJSU information"
            return action, action_input, None
        
        observation = None
        
        return action, action_input, observation
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("Conversation history reset")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history"""
        return self.conversation_history.copy()
