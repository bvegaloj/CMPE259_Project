"""
Unit Tests for SJSU Virtual Assistant Agent
Tests agent orchestrator and ReAct loop functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.agent.agent_orchestrator import AgentOrchestrator


class TestAgentOrchestrator(unittest.TestCase):
    """Test cases for AgentOrchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock LLM client
        self.mock_llm = Mock()
        self.mock_llm.model_name = "test-model"
        self.mock_llm.generate = Mock(return_value="Test response")
        
        # Create agent with mock LLM
        self.agent = AgentOrchestrator(self.mock_llm, max_iterations=3)
    
    def test_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.max_iterations, 3)
        self.assertEqual(self.agent.llm_client, self.mock_llm)
        self.assertIn('web_search', self.agent.tools)
        self.assertIn('database_query', self.agent.tools)
        self.assertEqual(len(self.agent.conversation_history), 0)
    
    def test_build_system_prompt(self):
        """Test system prompt building"""
        prompt = self.agent._build_system_prompt()
        
        self.assertIn("ReAct", prompt)
        self.assertIn("web_search", prompt)
        self.assertIn("database_query", prompt)
        self.assertIn("Thought:", prompt)
        self.assertIn("Action:", prompt)
        self.assertIn("Final Answer:", prompt)
    
    def test_build_user_prompt(self):
        """Test user prompt building"""
        query = "What is SJSU?"
        context = "Additional context"
        
        prompt = self.agent._build_user_prompt(query, context)
        
        self.assertIn(query, prompt)
        self.assertIn(context, prompt)
        self.assertIn("Question:", prompt)
    
    def test_parse_response_final_answer(self):
        """Test parsing response with final answer"""
        response = "Thought: I have the answer\nFinal Answer: SJSU is a university"
        
        action, action_input, observation = self.agent._parse_response(response)
        
        self.assertEqual(action, "Final Answer")
        self.assertIsNone(action_input)
        self.assertEqual(observation, "SJSU is a university")
    
    def test_parse_response_with_action(self):
        """Test parsing response with action"""
        response = "Thought: Need to search\nAction: web_search\nAction Input: SJSU information"
        
        action, action_input, observation = self.agent._parse_response(response)
        
        self.assertEqual(action, "web_search")
        self.assertEqual(action_input, "SJSU information")
        self.assertIsNone(observation)
    
    def test_parse_response_action_only(self):
        """Test parsing response with action but no input"""
        response = "Action: database_query"
        
        action, action_input, observation = self.agent._parse_response(response)
        
        self.assertEqual(action, "database_query")
        self.assertEqual(action_input, "SJSU information")  # Default fallback
    
    def test_reset_conversation(self):
        """Test conversation history reset"""
        self.agent.conversation_history = [{"role": "user", "content": "test"}]
        
        self.agent.reset_conversation()
        
        self.assertEqual(len(self.agent.conversation_history), 0)
    
    def test_get_conversation_history(self):
        """Test getting conversation history"""
        test_history = [{"role": "user", "content": "test"}]
        self.agent.conversation_history = test_history
        
        history = self.agent.get_conversation_history()
        
        self.assertEqual(history, test_history)
        self.assertIsNot(history, test_history)  # Should be a copy
    
    @patch('src.agent.agent_orchestrator.WebSearchTool')
    @patch('src.agent.agent_orchestrator.DatabaseQueryTool')
    def test_run_with_final_answer(self, mock_db_tool, mock_web_tool):
        """Test run method with immediate final answer"""
        # Mock LLM to return final answer
        self.mock_llm.generate.return_value = "Final Answer: SJSU is San Jose State University"
        
        result = self.agent.run("What is SJSU?")
        
        self.assertIn('query', result)
        self.assertIn('response', result)
        self.assertIn('reasoning_steps', result)
        self.assertIn('iterations', result)
        self.assertEqual(result['query'], "What is SJSU?")
        self.assertEqual(result['response'], "SJSU is San Jose State University")
        self.assertTrue(result['metadata']['completed'])
    
    @patch('src.agent.agent_orchestrator.WebSearchTool')
    @patch('src.agent.agent_orchestrator.DatabaseQueryTool')
    def test_run_max_iterations(self, mock_db_tool, mock_web_tool):
        """Test run method reaching max iterations"""
        # Mock LLM to return action without final answer
        self.mock_llm.generate.return_value = "Thought: Searching\nAction: web_search\nAction Input: SJSU"
        
        # Mock tool execution
        mock_web_instance = Mock()
        mock_web_instance.execute.return_value = "SJSU search result"
        mock_web_tool.return_value = mock_web_instance
        
        result = self.agent.run("What is SJSU?")
        
        self.assertEqual(result['iterations'], 3)  # Should hit max_iterations
        self.assertGreater(len(result['reasoning_steps']), 0)
    
    def test_update_prompt(self):
        """Test prompt updating with reasoning step"""
        initial_prompt = "Question: What is SJSU?"
        step = {
            'thought': 'I need to search',
            'action': 'web_search',
            'action_input': 'SJSU info',
            'observation': 'Found information'
        }
        
        updated_prompt = self.agent._update_prompt(initial_prompt, step)
        
        self.assertIn(initial_prompt, updated_prompt)
        self.assertIn('I need to search', updated_prompt)
        self.assertIn('web_search', updated_prompt)
        self.assertIn('Found information', updated_prompt)


class TestAgentTools(unittest.TestCase):
    """Test cases for agent tools integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_llm.model_name = "test-model"
        self.agent = AgentOrchestrator(self.mock_llm)
    
    def test_tools_initialization(self):
        """Test that tools are properly initialized"""
        self.assertIsNotNone(self.agent.tools.get('web_search'))
        self.assertIsNotNone(self.agent.tools.get('database_query'))
    
    def test_invalid_tool_name(self):
        """Test handling of invalid tool names"""
        response = "Action: invalid_tool\nAction Input: test"
        action, action_input, observation = self.agent._parse_response(response)
        
        self.assertEqual(action, "invalid_tool")
        # Agent should handle invalid tool gracefully in run method


class TestAgentEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_llm.model_name = "test-model"
        self.agent = AgentOrchestrator(self.mock_llm)
    
    def test_empty_query(self):
        """Test handling of empty query"""
        self.mock_llm.generate.return_value = "Final Answer: Please provide a question"
        
        result = self.agent.run("")
        
        self.assertIn('response', result)
    
    def test_llm_error_handling(self):
        """Test handling of LLM errors"""
        self.mock_llm.generate.side_effect = Exception("LLM Error")
        
        result = self.agent.run("What is SJSU?")
        
        self.assertIn('response', result)
        self.assertGreater(len(result['reasoning_steps']), 0)
    
    def test_malformed_response(self):
        """Test handling of malformed LLM response"""
        self.mock_llm.generate.return_value = "Random text without structure"
        
        action, action_input, observation = self.agent._parse_response("Random text")
        
        # Should handle gracefully without crashing
        self.assertIsNone(action)


if __name__ == '__main__':
    unittest.main()
