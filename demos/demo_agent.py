"""
Simple interactive demo of SJSU Agent
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.agent_orchestrator import AgentOrchestrator
from src.llm.model_loader import ModelLoader
from src.database.db_manager import DatabaseManager
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger('demo')


def demo_agent():
    """Interactive demo of the SJSU Agent"""
    
    print("\nSJSU VIRTUAL ASSISTANT - DEMO")
    print("\nInitializing agent...")
    
    # Load configuration
    config = Config()
    config.load_from_env()
    
    # Initialize database
    print("Connecting to database...")
    db_path = project_root / "data" / "sjsu_database.db"
    db_manager = DatabaseManager(
        db_path=str(db_path),
        collection_name='sjsu_docs'
    )
    
    # Load model (using Groq by default as it's fastest)
    print("Loading Groq Llama model...")
    model = ModelLoader.load_model('groq_llama', config=config)
    
    # Initialize agent
    agent = AgentOrchestrator(
        llm_client=model,
        db_manager=db_manager,
        config=config
    )
    
    print("Agent is ready!\n")
    print("Try these example queries:")
    print("  1. What are the CS program requirements?")
    print("  2. When are the application deadlines?")
    print("  3. What campus resources are available?")
    print("  4. What's the current SJSU tuition? (uses web search)")
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            # Get user input
            question = input("\nYou: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Query agent
            print("\nAgent: Thinking...")
            result = agent.run(query=question)
            
            # Extract and display the response
            if isinstance(result, dict):
                response = result.get('response', str(result))
            else:
                response = str(result)
            
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    demo_agent()
