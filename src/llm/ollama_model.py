"""
Ollama Model Client for SJSU Virtual Assistant
General-purpose client for any models hosted on Ollama
"""

import os
import json
from typing import List, Dict, Any, Optional
import requests


class OllamaClient:
    """Client for Ollama-hosted models"""
    
    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            model_name: Name of the model to use
            base_url: Ollama API base URL
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
        print(f"Initialized Ollama client with model: {model_name}")
        print(f"Ollama API URL: {self.api_url}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate a response using Ollama
        
        Args:
            system_prompt: System instruction
            user_prompt: User query
            conversation_history: Optional conversation context
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response text
            return result["message"]["content"]
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Error: Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
            print(error_msg)
            return error_msg
        except requests.exceptions.Timeout:
            error_msg = "Error: Request timed out. The model may be taking too long to respond."
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return error_msg
    
    def generate_with_streaming(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        """
        Generate a response with streaming
        
        Args:
            system_prompt: System instruction
            user_prompt: User query
            conversation_history: Optional conversation context
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks
        """
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # Call Ollama API with streaming
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                stream=True,
                timeout=120
            )
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
                        
        except requests.exceptions.ConnectionError:
            error_msg = f"Error: Could not connect to Ollama at {self.base_url}"
            print(error_msg)
            yield error_msg
        except Exception as e:
            error_msg = f"Error in streaming: {str(e)}"
            print(error_msg)
            yield error_msg
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Simple chat interface
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response text
        """
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["message"]["content"]
            
        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dict with model information
        """
        try:
            response = requests.post(
                f"{self.api_url}/show",
                json={"name": self.model_name},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                'model_name': self.model_name,
                'provider': 'Ollama',
                'base_url': self.base_url,
                'error': str(e)
            }
    
    def test_connection(self) -> bool:
        """
        Test if Ollama is running and accessible
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            print("Ollama connection successful")
            return True
        except Exception as e:
            print(f"Ollama connection failed: {str(e)}")
            return False
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.api_url}/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Pull/download a model in Ollama
        
        Args:
            model_name: Name of model to pull (defaults to self.model_name)
            
        Returns:
            True if successful, False otherwise
        """
        model = model_name or self.model_name
        
        try:
            print(f"Pulling model {model}...")
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": model},
                stream=True,
                timeout=300
            )
            
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    status = json.loads(line)
                    if "status" in status:
                        print(f"Status: {status['status']}")
            
            print(f"Successfully pulled model {model}")
            return True
            
        except Exception as e:
            print(f"Error pulling model: {str(e)}")
            return False
    
    def delete_model(self, model_name: str) -> bool:
        """
        Delete a model from Ollama
        
        Args:
            model_name: Name of model to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.api_url}/delete",
                json={"name": model_name}
            )
            response.raise_for_status()
            print(f"Successfully deleted model {model_name}")
            return True
        except Exception as e:
            print(f"Error deleting model: {str(e)}")
            return False
    
    def check_model_exists(self, model_name: Optional[str] = None) -> bool:
        """
        Check if a model exists in Ollama
        
        Args:
            model_name: Name of model to check (defaults to self.model_name)
            
        Returns:
            True if model exists, False otherwise
        """
        model = model_name or self.model_name
        models = self.list_models()
        return model in models


def get_ollama_base_models() -> List[str]:
    """
    Get list of popular base models available for Ollama
    
    Returns:
        List of model names
    """
    return [
        "llama3.1",
        "llama3.1:70b",
        "llama3",
        "llama2",
        "mistral",
        "mixtral",
        "phi3",
        "gemma",
        "codellama",
        "neural-chat",
        "starling-lm"
    ]
