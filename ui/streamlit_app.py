"""
SJSU Virtual Assistant - Streamlit UI
Interactive chat interface for the SJSU Virtual Assistant
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.agent_orchestrator import AgentOrchestrator
from src.llm.model_loader import ModelLoader
from src.database.db_manager import DatabaseManager
from src.utils.config import Config
from src.utils.logger import setup_logger


# Page configuration
st.set_page_config(
    page_title="SJSU Virtual Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = None
    
    if 'config' not in st.session_state:
        st.session_state.config = None
    
    if 'model_name' not in st.session_state:
        st.session_state.model_name = "groq_llama"
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []


def load_config():
    """Load configuration"""
    try:
        config = Config()
        config_file = project_root / "config" / "config.yaml"
        if config_file.exists():
            config.load_from_file(str(config_file))
        config.load_from_env()
        return config
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return None


def initialize_database(config):
    """Initialize database manager"""
    try:
        # Use absolute path for database
        db_path = project_root / "data" / "sjsu_database.db"
        db_manager = DatabaseManager(
            db_path=str(db_path),
            collection_name='sjsu_docs'
        )
        return db_manager
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return None


def initialize_agent(model_name, config, db_manager):
    """Initialize agent with selected model"""
    try:
        # Load model
        model = ModelLoader.load_model(model_name, config=config)
        
        # Create agent
        agent = AgentOrchestrator(
            llm_client=model,
            db_manager=db_manager,
            config=config
        )
        
        return agent
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None


def display_message(role, content):
    """Display a chat message"""
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)


def sidebar():
    """Render sidebar with settings"""
    with st.sidebar:
        st.title("Settings")
        
        # Model selection
        st.subheader("Model Selection")
        model_options = {
            "Groq Llama": "groq_llama",
            "Mistral": "mistral",
            "Llama (Ollama)": "llama",
            "Ollama": "ollama"
        }
        
        selected_model = st.selectbox(
            "Choose Model",
            options=list(model_options.keys()),
            index=0
        )
        
        new_model_name = model_options[selected_model]
        
        # Reinitialize if model changed
        if new_model_name != st.session_state.model_name:
            st.session_state.model_name = new_model_name
            st.session_state.agent = None
            st.rerun()
        
        st.divider()
        
        # Database stats
        st.subheader("Database Info")
        if st.session_state.db_manager:
            try:
                stats = st.session_state.db_manager.get_collection_stats()
                st.metric("Documents", stats.get('count', 0))
            except:
                st.info("Database statistics unavailable")
        
        st.divider()
        
        # Clear conversation
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        st.divider()
        
        # About
        st.subheader("About")
        st.info("""
        SJSU Virtual Assistant helps answer questions about:
        - Academics and courses
        - Campus events
        - Housing and facilities
        - General SJSU information
        """)


def main():
    """Main application"""
    st.title("SJSU Virtual Assistant")
    st.caption("Ask me anything about San Jose State University")
    
    # Initialize session state
    initialize_session_state()
    
    # Load configuration
    if st.session_state.config is None:
        with st.spinner("Loading configuration..."):
            st.session_state.config = load_config()
    
    if st.session_state.config is None:
        st.error("Failed to load configuration. Please check your setup.")
        return
    
    # Initialize database
    if st.session_state.db_manager is None:
        with st.spinner("Connecting to database..."):
            st.session_state.db_manager = initialize_database(st.session_state.config)
    
    if st.session_state.db_manager is None:
        st.error("Failed to connect to database. Please check your setup.")
        return
    
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner(f"Loading {st.session_state.model_name} model..."):
            st.session_state.agent = initialize_agent(
                st.session_state.model_name,
                st.session_state.config,
                st.session_state.db_manager
            )
    
    if st.session_state.agent is None:
        st.error("Failed to initialize agent. Please check your model configuration.")
        return
    
    # Render sidebar
    sidebar()
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(message['role'], message['content'])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about SJSU..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message("user", prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Update agent's conversation history before running
                    st.session_state.agent.conversation_history = st.session_state.conversation_history
                    
                    result = st.session_state.agent.run(query=prompt)
                    
                    # Extract response from result dict
                    if isinstance(result, dict):
                        response = result.get('response', str(result))
                    else:
                        response = str(result)
                    
                    # Update conversation history
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": prompt
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    # Display response
                    st.markdown(response)
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


if __name__ == "__main__":
    main()
