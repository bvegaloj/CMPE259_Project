"""
Mistral Model Client for SJSU Virtual Assistant
Provides interface to Mistral AI models via API
"""

import os
from typing import List, Dict, Any, Optional
from mistralai import Mistral


class MistralClient:
    """Client for Mistral AI models"""
    
    def __init__(self, model_name: str = "mistral-large-latest", api_key: Optional[str] = None):
        """
        Initialize Mistral client
        
        Args:
            model_name: Name of the Mistral model to use
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        # Initialize Mistral client
        self.client = Mistral(api_key=self.api_key)
        
        print(f"Initialized Mistral client with model: {model_name}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate a response using Mistral
        
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
            # Call Mistral API
            response = self.client.chat.complete(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response text
            return response.choices[0].message.content
            
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
            # Call Mistral API with streaming
            stream = self.client.chat.stream(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            for chunk in stream:
                if chunk.data.choices[0].delta.content is not None:
                    yield chunk.data.choices[0].delta.content
                    
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
            response = self.client.chat.complete(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
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
        return {
            'model_name': self.model_name,
            'provider': 'Mistral AI',
            'api_configured': self.api_key is not None
        }
    
    def test_connection(self) -> bool:
        """
        Test if the API connection works
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'Hello'",
                max_tokens=10
            )
            return "error" not in response.lower()
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False


def get_available_mistral_models() -> List[str]:
    """
    Get list of available Mistral models
    
    Returns:
        List of model names
    """
    return [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest",
        "mistral-tiny",
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b"
    ]
