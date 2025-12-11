"""
Database Tool Tests
Tests for database tool functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock


class TestDatabaseTool(unittest.TestCase):
    """Test DatabaseTool class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_db_manager = Mock()
    
    def test_tool_initialization(self):
        """Test database tool initialization"""
        from src.tools.database_tool import DatabaseTool
        
        tool = DatabaseTool(self.mock_db_manager)
        
        self.assertEqual(tool.db_manager, self.mock_db_manager)
        self.assertEqual(tool.name, "database_query")
    
    def test_execute_basic_query(self):
        """Test basic query execution"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        self.mock_db_manager.query.return_value = [
            {"content": "Test document 1", "category": "academics", "score": 0.95},
            {"content": "Test document 2", "category": "academics", "score": 0.85}
        ]
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query")
        
        self.assertIn("Test document 1", result)
        self.assertIn("Test document 2", result)
        self.mock_db_manager.query.assert_called_once()
    
    def test_execute_with_category_filter(self):
        """Test query with category filter"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        self.mock_db_manager.query_with_filter.return_value = [
            {"content": "Academic info", "category": "academics", "score": 0.9}
        ]
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query", category="academics")
        
        self.assertIn("Academic info", result)
        self.mock_db_manager.query_with_filter.assert_called_once()
    
    def test_execute_with_top_k(self):
        """Test query with custom top_k"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        self.mock_db_manager.query.return_value = [
            {"content": f"Document {i}", "category": "test", "score": 0.9 - i*0.1}
            for i in range(5)
        ]
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query", top_k=5)
        
        # Verify top_k was passed
        call_args = self.mock_db_manager.query.call_args
        self.assertEqual(call_args.kwargs.get('top_k') or call_args[1].get('top_k'), 5)
    
    def test_execute_empty_results(self):
        """Test handling of empty results"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        self.mock_db_manager.query.return_value = []
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query")
        
        self.assertIn("No results found", result)
    
    def test_execute_with_scores(self):
        """Test that results include relevance scores"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        self.mock_db_manager.query.return_value = [
            {"content": "High relevance", "category": "test", "score": 0.95},
            {"content": "Lower relevance", "category": "test", "score": 0.75}
        ]
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query")
        
        # Verify scores are included
        self.assertIn("0.95", result)
        self.assertIn("0.75", result)
    
    def test_query_by_category(self):
        """Test query_by_category method"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        self.mock_db_manager.query_with_filter.return_value = [
            {"content": "Category specific", "category": "events", "score": 0.9}
        ]
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.query_by_category("test query", "events")
        
        self.assertIn("Category specific", result)
        self.mock_db_manager.query_with_filter.assert_called_once_with(
            "test query", 
            category="events", 
            top_k=unittest.mock.ANY
        )
    
    def test_search_multiple_queries(self):
        """Test searching with multiple queries"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock to return different results for different queries
        def query_side_effect(query_text, **kwargs):
            if "academics" in query_text.lower():
                return [{"content": "Academic result", "category": "academics", "score": 0.9}]
            elif "events" in query_text.lower():
                return [{"content": "Event result", "category": "events", "score": 0.85}]
            return []
        
        self.mock_db_manager.query.side_effect = query_side_effect
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        queries = ["academics query", "events query"]
        result = tool.search_multiple_queries(queries)
        
        self.assertIn("Academic result", result)
        self.assertIn("Event result", result)
        self.assertEqual(self.mock_db_manager.query.call_count, 2)
    
    def test_get_description(self):
        """Test tool description"""
        from src.tools.database_tool import DatabaseTool
        
        tool = DatabaseTool(self.mock_db_manager)
        description = tool.get_description()
        
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 0)
        self.assertIn("database", description.lower())
    
    def test_get_parameters(self):
        """Test tool parameters"""
        from src.tools.database_tool import DatabaseTool
        
        tool = DatabaseTool(self.mock_db_manager)
        params = tool.get_parameters()
        
        self.assertIsInstance(params, dict)
        self.assertIn("query", params)
    
    def test_error_handling(self):
        """Test error handling"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock to raise exception
        self.mock_db_manager.query.side_effect = Exception("Database error")
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query")
        
        self.assertIn("error", result.lower())
    
    def test_format_results(self):
        """Test result formatting"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock with various result types
        self.mock_db_manager.query.return_value = [
            {
                "content": "Long content " * 50,  # Very long content
                "category": "academics",
                "score": 0.95,
                "metadata": {"source": "test.pdf"}
            }
        ]
        
        # Test
        tool = DatabaseTool(self.mock_db_manager)
        result = tool.execute("test query")
        
        # Verify formatting
        self.assertIsInstance(result, str)
        self.assertIn("academics", result)
        self.assertIn("0.95", result)


class TestDatabaseToolIntegration(unittest.TestCase):
    """Test database tool integration scenarios"""
    
    @patch('src.tools.database_tool.DatabaseManager')
    def test_integration_with_real_db_manager(self, mock_db_class):
        """Test integration with database manager"""
        from src.tools.database_tool import DatabaseTool
        
        # Setup mock
        mock_db_instance = Mock()
        mock_db_instance.query.return_value = [
            {"content": "Integration test", "category": "test", "score": 0.9}
        ]
        mock_db_class.return_value = mock_db_instance
        
        # Test
        tool = DatabaseTool(mock_db_instance)
        result = tool.execute("integration query")
        
        self.assertIn("Integration test", result)
    
    def test_category_validation(self):
        """Test category validation"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        mock_db.query_with_filter.return_value = []
        
        tool = DatabaseTool(mock_db)
        
        # Test valid categories
        valid_categories = ["academics", "events", "housing", "facilities", "general"]
        for category in valid_categories:
            result = tool.execute("test", category=category)
            self.assertIsInstance(result, str)
    
    def test_concurrent_queries(self):
        """Test handling multiple concurrent queries"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        mock_db.query.return_value = [
            {"content": "Result", "category": "test", "score": 0.8}
        ]
        
        tool = DatabaseTool(mock_db)
        
        # Execute multiple queries
        queries = [f"query {i}" for i in range(5)]
        results = [tool.execute(q) for q in queries]
        
        self.assertEqual(len(results), 5)
        self.assertEqual(mock_db.query.call_count, 5)


class TestDatabaseToolEdgeCases(unittest.TestCase):
    """Test edge cases for database tool"""
    
    def test_empty_query(self):
        """Test handling of empty query"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        tool = DatabaseTool(mock_db)
        
        result = tool.execute("")
        
        # Should handle gracefully
        self.assertIsInstance(result, str)
    
    def test_very_long_query(self):
        """Test handling of very long query"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        mock_db.query.return_value = []
        
        tool = DatabaseTool(mock_db)
        long_query = "test " * 1000
        
        result = tool.execute(long_query)
        
        self.assertIsInstance(result, str)
    
    def test_special_characters_in_query(self):
        """Test handling of special characters"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        mock_db.query.return_value = []
        
        tool = DatabaseTool(mock_db)
        special_query = "test @#$%^&*() query"
        
        result = tool.execute(special_query)
        
        self.assertIsInstance(result, str)
    
    def test_none_results(self):
        """Test handling of None results from database"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        mock_db.query.return_value = None
        
        tool = DatabaseTool(mock_db)
        result = tool.execute("test")
        
        self.assertIn("No results", result)
    
    def test_malformed_results(self):
        """Test handling of malformed results"""
        from src.tools.database_tool import DatabaseTool
        
        mock_db = Mock()
        # Return results missing required fields
        mock_db.query.return_value = [
            {"content": "Test"},  # Missing category and score
            {"category": "test", "score": 0.9}  # Missing content
        ]
        
        tool = DatabaseTool(mock_db)
        result = tool.execute("test")
        
        # Should handle gracefully without crashing
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
