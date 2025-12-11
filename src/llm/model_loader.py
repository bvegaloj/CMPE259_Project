"""
Model Loader for SJSU Virtual Assistant
Factory for loading different LLM clients
"""

from typing import Optional
from src.llm.mistral_model import MistralClient
from src.llm.llama_model import LlamaClient
from src.llm.groq_llama_model import GroqLlamaClient


class ModelLoader:
    """Factory class for loading LLM clients"""
    
    SUPPORTED_MODELS = {
        'mistral': ['mistral-large-latest', 'mistral-medium-latest', 'mistral-small-latest'],
        'llama': ['llama3.1', 'llama3.1:70b', 'llama3', 'llama2'],
        'groq_llama': ['llama-3.3-70b-versatile', 'llama-3.1-70b-versatile', 'llama-3.1-8b-instant']
    }
    
    @staticmethod
    def load_model(model_type: str, model_name: Optional[str] = None, **kwargs):
        """
        Load an LLM client
        
        Args:
            model_type: Type of model ('mistral', 'llama', 'groq_llama')
            model_name: Specific model name (optional)
            **kwargs: Additional arguments for the client
            
        Returns:
            LLM client instance
        """
        model_type = model_type.lower()
        
        if model_type == 'mistral':
            default_model = 'mistral-large-latest'
            return MistralClient(
                model_name=model_name or default_model,
                api_key=kwargs.get('api_key')
            )
        
        elif model_type == 'llama':
            default_model = 'llama3.1'
            return LlamaClient(
                model_name=model_name or default_model,
                base_url=kwargs.get('base_url', 'http://localhost:11434')
            )
        
        elif model_type == 'groq_llama' or model_type == 'groq':
            default_model = 'llama-3.3-70b-versatile'
            return GroqLlamaClient(
                model_name=model_name or default_model,
                api_key=kwargs.get('api_key')
            )
        
        else:
            raise ValueError(
                f"Unsupported model type: {model_type}. "
                f"Supported types: {list(ModelLoader.SUPPORTED_MODELS.keys())}"
            )
    
    @staticmethod
    def get_supported_models():
        """
        Get dictionary of supported models
        
        Returns:
            Dict mapping model types to available models
        """
        return ModelLoader.SUPPORTED_MODELS.copy()
    
    @staticmethod
    def list_model_types():
        """
        Get list of supported model types
        
        Returns:
            List of model type strings
        """
        return list(ModelLoader.SUPPORTED_MODELS.keys())
    
    @staticmethod
    def validate_model(model_type: str, model_name: str) -> bool:
        """
        Check if a model type and name combination is supported
        
        Args:
            model_type: Type of model
            model_name: Name of model
            
        Returns:
            True if supported, False otherwise
        """
        model_type = model_type.lower()
        
        if model_type not in ModelLoader.SUPPORTED_MODELS:
            return False
        
        # For llama models, allow any name (Ollama can have custom models)
        if model_type == 'llama':
            return True
        
        # For Mistral and Groq, check if model name is in supported list
        return model_name in ModelLoader.SUPPORTED_MODELS[model_type]
    
    @staticmethod
    def get_default_model(model_type: str) -> str:
        """
        Get the default model name for a model type
        
        Args:
            model_type: Type of model
            
        Returns:
            Default model name
        """
        defaults = {
            'mistral': 'mistral-large-latest',
            'llama': 'llama3.1',
            'groq_llama': 'llama-3.3-70b-versatile',
            'groq': 'llama-3.3-70b-versatile'
        }
        
        return defaults.get(model_type.lower(), 'mistral-large-latest')


def load_model_from_config(config: dict):
    """
    Load a model from a configuration dictionary
    
    Args:
        config: Configuration dict with 'model_type', 'model_name', etc.
        
    Returns:
        LLM client instance
    """
    model_type = config.get('model_type', 'mistral')
    model_name = config.get('model_name')
    
    # Extract additional kwargs
    kwargs = {}
    if 'api_key' in config:
        kwargs['api_key'] = config['api_key']
    if 'base_url' in config:
        kwargs['base_url'] = config['base_url']
    
    return ModelLoader.load_model(model_type, model_name, **kwargs)


def get_model_info(model_type: str) -> dict:
    """
    Get information about a model type
    
    Args:
        model_type: Type of model
        
    Returns:
        Dict with model information
    """
    info = {
        'mistral': {
            'provider': 'Mistral AI',
            'requires_api_key': True,
            'supports_streaming': True,
            'description': 'Mistral AI commercial models via API'
        },
        'llama': {
            'provider': 'Ollama (Local)',
            'requires_api_key': False,
            'supports_streaming': True,
            'description': 'Local Llama models via Ollama'
        },
        'groq_llama': {
            'provider': 'Groq',
            'requires_api_key': True,
            'supports_streaming': True,
            'description': 'Llama models via Groq cloud API'
        }
    }
    
    return info.get(model_type.lower(), {})
