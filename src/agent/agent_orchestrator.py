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
    
    def __init__(self, llm_client, db_manager=None, config=None, max_iterations: int = 10):
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
                
                # ENFORCE TOOL USAGE: On first iteration, reject Final Answer without tool usage
                # This prevents hallucination when the model skips database lookup
                if action == 'Final Answer' and iteration == 1:
                    print("WARNING: Model tried to answer without using tools. Forcing database query...")
                    # Force a database query with the original question
                    action = 'database_query'
                    action_input = query
                    step['action'] = action
                    step['action_input'] = action_input
                    step['observation'] = None  # Will be filled by tool execution
                
                # Check if we have a final answer (only after first iteration)
                if action == 'Final Answer' and iteration > 1:
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
                        print(f"TOOL OBSERVATION FOR LLM:")
                        print(observation)
                        
                        # Print truncated version for console
                        print(f"Observation: {observation[:200]}..." if len(str(observation)) > 200 else f"Observation: {observation}")
                        
                        # AUTO-FALLBACK: Check if database results are relevant to the query
                        if action == 'database_query':
                            should_fallback = False
                            fallback_reason = ""
                            
                            # Case 1: No results found
                            if 'No information found' in observation:
                                should_fallback = True
                                fallback_reason = "no results"
                            
                            # Case 2: Results don't match query keywords (irrelevant results)
                            else:
                                # Smart relevance detection - no manual trigger list needed
                                query_lower = query.lower()
                                obs_lower = observation.lower()
                                
                                # Common stop words to ignore when checking relevance
                                stop_words = {'what', 'where', 'when', 'how', 'who', 'which', 'is', 'are', 'was', 'were', 
                                             'the', 'a', 'an', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with',
                                             'do', 'does', 'did', 'can', 'could', 'would', 'should', 'will',
                                             'i', 'me', 'my', 'need', 'want', 'get', 'find', 'about', 'tell',
                                             'sjsu', 'san', 'jose', 'state', 'university', 'enroll', 'apply',
                                             'requirements', 'requirement', 'program', 'course', 'class'}
                                
                                # Extract significant words from query (2+ chars, not stop words)
                                query_words = set(word.strip('?.,!') for word in query_lower.split() 
                                                 if len(word) > 2 and word.strip('?.,!') not in stop_words)
                                
                                # Check how many query words appear in the observation
                                matches = sum(1 for word in query_words if word in obs_lower)
                                
                                # If less than half of significant query words are in results, fallback
                                if query_words and matches < len(query_words) * 0.5:
                                    should_fallback = True
                                    missing_words = [w for w in query_words if w not in obs_lower]
                                    fallback_reason = f"query terms not in results: {', '.join(missing_words[:3])}"
                                
                                # Also check conversation history for context on vague queries
                                if not should_fallback and len(query.split()) <= 5 and self.conversation_history:
                                    # Extract terms from recent conversation
                                    conv_terms = set()
                                    for msg in self.conversation_history[-2:]:
                                        msg_lower = msg.get('content', '').lower()
                                        for word in msg_lower.split():
                                            word = word.strip('?.,!')
                                            if len(word) > 3 and word not in stop_words:
                                                conv_terms.add(word)
                                    
                                    # If conversation has specific terms not in results, fallback
                                    conv_matches = sum(1 for term in conv_terms if term in obs_lower)
                                    if conv_terms and conv_matches < len(conv_terms) * 0.3:
                                        should_fallback = True
                                        fallback_reason = "conversation context not in results"
                            
                            if should_fallback:
                                print(f"\nDatabase results not relevant ({fallback_reason}) - trying web_search")
                                
                                # Build optimized search query based on query type
                                query_lower = query.lower()
                                location_words = ['where', 'location', 'building', 'address', 'find', 'directions', 'located']
                                is_location_query = any(word in query_lower for word in location_words)
                                
                                if is_location_query:
                                    # For location queries, search for "SJSU [office name] office location address building"
                                    # Extract the subject (e.g., "financial aid" from "where is the financial aid building")
                                    subject = query_lower
                                    for word in location_words + ['the', 'is', 'are', 'sjsu', '?', 'what']:
                                        subject = subject.replace(word, ' ')
                                    subject = ' '.join(subject.split()).strip()
                                    
                                    # If subject is empty/vague, try to get it from conversation history
                                    if len(subject) < 3 and self.conversation_history:
                                        for msg in reversed(self.conversation_history[-4:]):
                                            msg_lower = msg.get('content', '').lower()
                                            # Look for key subjects in recent conversation
                                            if 'financial aid' in msg_lower:
                                                subject = 'financial aid'
                                                break
                                            elif 'housing' in msg_lower:
                                                subject = 'housing'
                                                break
                                            elif 'parking' in msg_lower:
                                                subject = 'parking'
                                                break
                                            elif 'registrar' in msg_lower:
                                                subject = 'registrar'
                                                break
                                            elif 'bookstore' in msg_lower:
                                                subject = 'bookstore'
                                                break
                                    
                                    web_search_query = f"SJSU {subject} office location address building"
                                else:
                                    web_search_query = f"SJSU {query}"
                                
                                try:
                                    observation = self.tools['web_search'].execute(web_search_query)
                                    step['action'] = 'web_search'
                                    step['action_input'] = web_search_query
                                    step['observation'] = observation
                                    print(f"Web search completed")
                                except Exception as web_error:
                                    observation = f"I couldn't find specific information about this. Please check sjsu.edu or contact the university directly."
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
        
        # If no final answer, construct one from the best observation
        if not final_answer and reasoning_steps:
            # Find the best observation (from database or web search)
            best_observation = None
            for step in reasoning_steps:
                obs = step.get('observation', '')
                if obs and '>>> MOST RELEVANT ANSWER >>>' in str(obs):
                    best_observation = obs
                    break
                elif obs and not best_observation:
                    best_observation = obs
            
            if best_observation:
                # Clean up the observation to create a readable response
                final_answer = self._format_observation_as_answer(best_observation)
            else:
                final_answer = reasoning_steps[-1].get('thought', 'Unable to generate response')
        
        
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
        """Build the initial user prompt with few-shot example to prevent first-query hallucination"""
        # Few-shot example to guide proper tool usage
        few_shot_example = """Here's an example of how to properly answer a question:

Question: What are the prerequisites for CMPE 259?

Thought: I need to find information about CMPE 259 prerequisites. I should query the SJSU database first.
Action: database_query
Action Input: CMPE 259 prerequisites
Observation: >>> MOST RELEVANT ANSWER >>> CMPE 259 - Natural Language Processing: Prerequisites: CMPE 252 or CMPE 255 or CMPE 257, or instructor consent.
Thought: I found the prerequisites in the database. I will provide the exact information.
Final Answer: The prerequisites for CMPE 259 (Natural Language Processing) are: CMPE 252 or CMPE 255 or CMPE 257, or instructor consent.

---
Now answer the following question using the same approach:

"""
        prompt = few_shot_example
        
        # Add recent conversation context for follow-up questions
        if self.conversation_history and len(self.conversation_history) >= 2:
            # Include last exchange (1 user question + 1 assistant response)
            recent_context = self.conversation_history[-2:]
            prompt += "Recent conversation for context:\n"
            for msg in recent_context:
                role = msg.get('role', 'unknown').capitalize()
                content = msg.get('content', '')[:200]  # Truncate to avoid too much context
                prompt += f"{role}: {content}\n"
            prompt += "\n"
        
        prompt += f"Question: {query}\n\n"
        if context:
            prompt += f"Additional Context: {context}\n\n"
        prompt += "Thought:"
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
        
        # Look for Action Input - improved regex to handle multi-line and stop at various markers
        input_match = re.search(r'Action Input:\s*["\']?(.+?)["\']?\s*(?:\n\s*(?:Observation|Thought|Final Answer|Action)|\Z)', response, re.IGNORECASE | re.DOTALL)
        if input_match:
            action_input = input_match.group(1).strip()
            # Clean up the action input - remove any trailing "Observation:" or similar
            action_input = re.sub(r'\s*Observation\s*:.*$', '', action_input, flags=re.IGNORECASE | re.DOTALL)
            action_input = re.sub(r'\s*Thought\s*:.*$', '', action_input, flags=re.IGNORECASE | re.DOTALL)
            # Remove quotes if present
            action_input = action_input.strip('"\'')
            # Limit length to prevent long queries
            if len(action_input) > 200:
                action_input = action_input[:200]
        
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
    
    def _format_observation_as_answer(self, observation: str) -> str:
        """
        Format a raw database or web search observation into a clean, readable response.
        Extracts the most relevant information and removes metadata markers.
        """
        # Extract the first/best result content
        obs_str = str(observation)
        
        # Check if it's a web search result (Summary + Result format)
        if 'Summary:' in obs_str:
            # Extract the AI-generated summary from web search
            match = re.search(r'Summary:\s*(.+?)(?:\n\s*Result \d+:|\Z)', obs_str, re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Also try to extract source URL for citation
                url_match = re.search(r'URL:\s*(https?://[^\n]+)', obs_str)
                if url_match and 'sjsu.edu' in url_match.group(1):
                    return f"{summary}\n\nSource: {url_match.group(1)}"
                return summary
        
        # Check if it's web search without summary but with results
        if 'Result 1:' in obs_str and 'Content:' in obs_str:
            # Extract title and content from first result
            title_match = re.search(r'Title:\s*([^\n]+)', obs_str)
            content_match = re.search(r'Content:\s*(.+?)(?:\n\s*Result \d+:|\Z)', obs_str, re.DOTALL)
            url_match = re.search(r'URL:\s*(https?://[^\n]+)', obs_str)
            
            if content_match:
                content = content_match.group(1).strip()
                # Clean up truncation markers
                content = content.replace('...', '')
                
                # Try to extract specific info like addresses, phone numbers
                response = content
                if url_match:
                    response += f"\n\nSource: {url_match.group(1)}"
                return response
        
        # Check if it's a Q&A format (FAQ)
        if 'Q:' in obs_str and 'A:' in obs_str:
            # Extract the answer from FAQ format
            match = re.search(r'A:\s*(.+?)(?:\n\nResult|\Z)', obs_str, re.DOTALL)
            if match:
                answer = match.group(1).strip()
                return answer
        
        # Check if it's a course/prerequisite format
        if 'Prerequisites:' in obs_str:
            # Extract course info
            course_match = re.search(r'([A-Z]{2,4}\s*\d{3})\s*-\s*([^:]+):\s*Prerequisites:\s*([^.]+\.?)', obs_str)
            if course_match:
                course_code = course_match.group(1)
                course_name = course_match.group(2).strip()
                prereqs = course_match.group(3).strip()
                return f"The prerequisites for {course_code} ({course_name}) are: {prereqs}"
        
        # Check if it's a scholarship format
        if 'Scholarship:' in obs_str:
            scholarships = []
            for match in re.finditer(r'Scholarship:\s*([^\n]+)\nAmount:\s*\$?([\d,]+)', obs_str):
                name = match.group(1).strip()
                amount = match.group(2).strip()
                scholarships.append(f"• {name} (${amount})")
            if scholarships:
                return "Available scholarships:\n" + "\n".join(scholarships[:5])
        
        # Check if it's a club format
        if 'Club:' in obs_str:
            clubs = []
            for match in re.finditer(r'Club:\s*([^\n]+)\n.*?Description:\s*([^\n]+)', obs_str, re.DOTALL):
                name = match.group(1).strip()
                desc = match.group(2).strip()
                clubs.append(f"• {name}: {desc}")
            if clubs:
                return "Student clubs:\n" + "\n".join(clubs[:5])
        
        # Check if it's a deadline format
        if 'Deadline:' in obs_str:
            deadlines = []
            for match in re.finditer(r'Deadline:\s*([^\n]+)\nDate:\s*([^\n]+)', obs_str):
                dtype = match.group(1).strip()
                date = match.group(2).strip()
                deadlines.append(f"• {dtype}: {date}")
            if deadlines:
                return "Important deadlines:\n" + "\n".join(deadlines[:5])
        
        # Check if it's a resource format
        if 'Resource:' in obs_str:
            resources = []
            for match in re.finditer(r'Resource:\s*([^\n]+)\n.*?Description:\s*([^\n]+)', obs_str, re.DOTALL):
                name = match.group(1).strip()
                desc = match.group(2).strip()
                resources.append(f"• {name}: {desc}")
            if resources:
                return "Campus resources:\n" + "\n".join(resources[:5])
        
        # Check if it's a program format
        if 'Program:' in obs_str or '(MS):' in obs_str or '(BS):' in obs_str:
            # Extract program info
            match = re.search(r'([^:]+\([A-Z]{2,3}\)):\s*(.+?)(?:\n\nResult|\Z)', obs_str, re.DOTALL)
            if match:
                return f"{match.group(1)}: {match.group(2).strip()[:300]}"
        
        # Fallback: Clean up raw observation
        # Remove markers and metadata
        cleaned = re.sub(r'>>>\s*MOST RELEVANT ANSWER\s*>>>', '', obs_str)
        cleaned = re.sub(r'Result \d+ \[[^\]]+\] \(relevance: [\d.]+\):', '', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)  # Remove extra blank lines
        cleaned = cleaned.strip()
        
        # Return first 500 chars of cleaned content
        if len(cleaned) > 500:
            cleaned = cleaned[:500] + "..."
        
        return cleaned if cleaned else "I found relevant information but couldn't format it properly. Please try rephrasing your question."
