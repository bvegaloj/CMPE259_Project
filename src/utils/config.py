"""
Configuration Management for SJSU Virtual Assistant
Handles configuration loading and validation
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the SJSU Virtual Assistant"""
    
    # Default configuration values
    DEFAULTS = {
        'model_type': 'groq_llama',
        'model_name': 'llama-3.3-70b-versatile',
        'temperature': 0.7,
        'max_tokens': 1024,
        'max_iterations': 5,
        'db_path': './data/chroma_db',
        'embedding_model': 'all-MiniLM-L6-v2',
        'ollama_base_url': 'http://localhost:11434'
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Optional path to config JSON file
        """
        self.config = self.DEFAULTS.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
        
        # Load environment variables
        self.load_from_env()
    
    def load_from_file(self, config_path: str):
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to config file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Update config with file values
            self.config.update(file_config)
            print(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            print(f"Error loading config file: {str(e)}")
    
    def load_from_env(self):
        """Load configuration from environment variables"""
        
        # API Keys
        if os.getenv('MISTRAL_API_KEY'):
            self.config['mistral_api_key'] = os.getenv('MISTRAL_API_KEY')
        
        if os.getenv('GROQ_API_KEY'):
            self.config['groq_api_key'] = os.getenv('GROQ_API_KEY')
        
        # Model settings
        if os.getenv('MODEL_TYPE'):
            self.config['model_type'] = os.getenv('MODEL_TYPE')
        
        if os.getenv('MODEL_NAME'):
            self.config['model_name'] = os.getenv('MODEL_NAME')
        
        if os.getenv('TEMPERATURE'):
            self.config['temperature'] = float(os.getenv('TEMPERATURE'))
        
        if os.getenv('MAX_TOKENS'):
            self.config['max_tokens'] = int(os.getenv('MAX_TOKENS'))
        
        # Database settings
        if os.getenv('DB_PATH'):
            self.config['db_path'] = os.getenv('DB_PATH')
        
        if os.getenv('OLLAMA_BASE_URL'):
            self.config['ollama_base_url'] = os.getenv('OLLAMA_BASE_URL')
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values
        
        Returns:
            Dict of all config values
        """
        return self.config.copy()
    
    def save_to_file(self, config_path: str):
        """
        Save configuration to JSON file
        
        Args:
            config_path: Path to save config file
        """
        try:
            # Create directory if needed
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Don't save API keys to file
            safe_config = {k: v for k, v in self.config.items() 
                          if 'api_key' not in k.lower()}
            
            with open(config_path, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            print(f"Saved configuration to {config_path}")
            
        except Exception as e:
            print(f"Error saving config file: {str(e)}")
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check model type
        valid_model_types = ['mistral', 'llama', 'groq_llama', 'groq']
        if self.config['model_type'] not in valid_model_types:
            errors.append(f"Invalid model_type: {self.config['model_type']}")
        
        # Check API keys for cloud models
        if self.config['model_type'] == 'mistral':
            if not self.config.get('mistral_api_key'):
                errors.append("MISTRAL_API_KEY not set for Mistral model")
        
        if self.config['model_type'] in ['groq_llama', 'groq']:
            if not self.config.get('groq_api_key'):
                errors.append("GROQ_API_KEY not set for Groq model")
        
        # Check numeric values
        if not 0 <= self.config['temperature'] <= 2:
            errors.append(f"Temperature must be between 0 and 2: {self.config['temperature']}")
        
        if self.config['max_tokens'] <= 0:
            errors.append(f"max_tokens must be positive: {self.config['max_tokens']}")
        
        if self.config['max_iterations'] <= 0:
            errors.append(f"max_iterations must be positive: {self.config['max_iterations']}")
        
        return len(errors) == 0, errors
    
    def print_config(self):
        """Print current configuration (excluding API keys)"""
        print("\nCurrent Configuration:")
        print("=" * 50)
        
        for key, value in sorted(self.config.items()):
            # Hide API keys
            if 'api_key' in key.lower():
                display_value = '***' if value else 'Not set'
            else:
                display_value = value
            
            print(f"{key}: {display_value}")
        
        print("=" * 50)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Convenience function to load configuration
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Config instance
    """
    return Config(config_path)


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration values
    
    Returns:
        Dict of default config values
    """
    return Config.DEFAULTS.copy()
