"""
Friendli.ai client wrapper for fast LLM inference.
"""
import os
import time
from typing import Optional, List, Dict, Any

try:
    import friendli
    FRIENDLI_AVAILABLE = True
except ImportError:
    FRIENDLI_AVAILABLE = False


class FriendliClient:
    """Client for Friendli.ai API with fast inference."""
    
    def __init__(self):
        self.api_key = os.getenv("FRIENDLI_API_KEY") or os.getenv("FRIENDLI_TOKEN")
        self.url = os.getenv("FRIENDLI_URL", "https://api.friendli.ai/v1")
        self.default_model = os.getenv("FRIENDLI_MODEL", "meta-llama-3.1-70b-instruct")
        
        self.client = None
        if FRIENDLI_AVAILABLE and self.api_key:
            try:
                friendli.api_key = self.api_key
                if self.url != "https://api.friendli.ai/v1":
                    friendli.base_url = self.url
                self.client = friendli
            except Exception as e:
                print(f"Warning: Failed to initialize Friendli client: {e}")
    
    def is_available(self) -> bool:
        """Check if Friendli client is available."""
        return self.client is not None
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate completion using Friendli.ai.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Model to use (defaults to meta-llama-3.1-70b-instruct)
            
        Returns:
            Dictionary with text, latency_ms, and metadata
        """
        if not self.client:
            raise Exception("Friendli client not initialized")
        
        start_time = time.time()
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Use specified model or default
        model_name = model or self.default_model
        
        try:
            response = friendli.ChatCompletion.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "text": response.choices[0].message.content,
                "latency_ms": round(latency_ms, 2),
                "model": model_name,
                "provider": "Friendli.ai",
                "success": True
            }
        except Exception as e:
            raise Exception(f"Friendli API error: {str(e)}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Model to use
            
        Returns:
            Dictionary with text, latency_ms, and metadata
        """
        if not self.client:
            raise Exception("Friendli client not initialized")
        
        start_time = time.time()
        model_name = model or self.default_model
        
        try:
            response = friendli.ChatCompletion.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "text": response.choices[0].message.content,
                "latency_ms": round(latency_ms, 2),
                "model": model_name,
                "provider": "Friendli.ai",
                "success": True
            }
        except Exception as e:
            raise Exception(f"Friendli API error: {str(e)}")
