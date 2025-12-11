"""
Groq Llama Model Client for SJSU Virtual Assistant
Provides interface to Groq's Llama models via API
"""

import os
from typing import List, Dict, Any, Optional
from groq import Groq


class GroqLlamaClient:
    """Client for Groq Llama models"""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", api_key: Optional[str] = None):
        """
        Initialize Groq Llama client
        
        Args:
            model_name: Name of the Groq model to use
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        
        print(f"Initialized Groq Llama client with model: {model_name}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate a response using Groq Llama
        
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
            # Filter to ensure only valid message dicts are added
            for msg in conversation_history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append(msg)
        
        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
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
            # Call Groq API with streaming
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
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
            response = self.client.chat.completions.create(
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
            'provider': 'Groq',
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


def get_available_groq_models() -> List[str]:
    """
    Get list of available Groq Llama models
    
    Returns:
        List of model names
    """
    return [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192"
    ]
