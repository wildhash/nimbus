"""
Model router with Friendli.ai as primary and AWS Bedrock as fallback.
Measures latency and logs provider usage.
"""
import os
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .friendli import FriendliClient
from .bedrock import BedrockClient


@dataclass
class LLMResponse:
    """Response from LLM with metadata."""
    text: str
    provider: str
    latency_ms: float
    model: str
    success: bool = True
    error: Optional[str] = None


class ModelRouter:
    """
    Routes LLM requests to Friendli.ai (primary) or AWS Bedrock (fallback).
    Tracks latency and provider usage.
    """
    
    def __init__(self):
        self.use_friendli = os.getenv("USE_FRIENDLI", "1") == "1"
        
        # Initialize clients
        self.friendli = FriendliClient()
        self.bedrock = BedrockClient()
        
        # Statistics
        self.stats = {
            "friendli_calls": 0,
            "bedrock_calls": 0,
            "mock_calls": 0,
            "total_latency_ms": 0.0,
            "call_count": 0
        }
    
    def llm_complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model_hint: Optional[str] = None,
        prefer_provider: Optional[str] = None
    ) -> LLMResponse:
        """
        Complete a prompt using available LLM provider.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            model_hint: Optional model name hint
            prefer_provider: Prefer 'friendli' or 'bedrock' if available
            
        Returns:
            LLMResponse with text, provider, latency, and metadata
        """
        providers = self._determine_provider_order(prefer_provider)
        last_error = None
        
        for provider in providers:
            try:
                if provider == "friendli" and self.friendli.is_available():
                    result = self.friendli.complete(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        model=model_hint
                    )
                    self._update_stats("friendli", result["latency_ms"])
                    return LLMResponse(
                        text=result["text"],
                        provider=result["provider"],
                        latency_ms=result["latency_ms"],
                        model=result["model"],
                        success=True
                    )
                
                elif provider == "bedrock" and self.bedrock.is_available():
                    result = self.bedrock.complete(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        model=model_hint
                    )
                    self._update_stats("bedrock", result["latency_ms"])
                    return LLMResponse(
                        text=result["text"],
                        provider=result["provider"],
                        latency_ms=result["latency_ms"],
                        model=result["model"],
                        success=True
                    )
            
            except Exception as e:
                last_error = e
                print(f"Provider {provider} failed: {str(e)}")
                continue
        
        # All providers failed, return mock response
        self._update_stats("mock", 0)
        return LLMResponse(
            text="I apologize, but I'm unable to connect to the LLM providers at the moment. Please check your API credentials and try again.",
            provider="mock",
            latency_ms=0.0,
            model="mock",
            success=False,
            error=str(last_error) if last_error else "No providers available"
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model_hint: Optional[str] = None,
        prefer_provider: Optional[str] = None
    ) -> LLMResponse:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model_hint: Optional model name hint
            prefer_provider: Prefer 'friendli' or 'bedrock' if available
            
        Returns:
            LLMResponse with text, provider, latency, and metadata
        """
        providers = self._determine_provider_order(prefer_provider)
        last_error = None
        
        for provider in providers:
            try:
                if provider == "friendli" and self.friendli.is_available():
                    result = self.friendli.chat(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        model=model_hint
                    )
                    self._update_stats("friendli", result["latency_ms"])
                    return LLMResponse(
                        text=result["text"],
                        provider=result["provider"],
                        latency_ms=result["latency_ms"],
                        model=result["model"],
                        success=True
                    )
                
                elif provider == "bedrock" and self.bedrock.is_available():
                    result = self.bedrock.chat(
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        model=model_hint
                    )
                    self._update_stats("bedrock", result["latency_ms"])
                    return LLMResponse(
                        text=result["text"],
                        provider=result["provider"],
                        latency_ms=result["latency_ms"],
                        model=result["model"],
                        success=True
                    )
            
            except Exception as e:
                last_error = e
                print(f"Provider {provider} failed: {str(e)}")
                continue
        
        # All providers failed
        self._update_stats("mock", 0)
        return LLMResponse(
            text="I apologize, but I'm unable to connect to the LLM providers at the moment.",
            provider="mock",
            latency_ms=0.0,
            model="mock",
            success=False,
            error=str(last_error) if last_error else "No providers available"
        )
    
    def _determine_provider_order(self, prefer_provider: Optional[str]) -> List[str]:
        """Determine the order of providers to try."""
        if prefer_provider == "friendli" and self.use_friendli:
            return ["friendli", "bedrock"]
        elif prefer_provider == "bedrock":
            return ["bedrock", "friendli"]
        elif self.use_friendli:
            # Default: try Friendli first, then Bedrock
            return ["friendli", "bedrock"]
        else:
            # Friendli disabled, use Bedrock only
            return ["bedrock"]
    
    def _update_stats(self, provider: str, latency_ms: float):
        """Update usage statistics."""
        self.stats["call_count"] += 1
        self.stats["total_latency_ms"] += latency_ms
        
        if provider == "friendli":
            self.stats["friendli_calls"] += 1
        elif provider == "bedrock":
            self.stats["bedrock_calls"] += 1
        elif provider == "mock":
            self.stats["mock_calls"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        avg_latency = 0.0
        if self.stats["call_count"] > 0:
            avg_latency = self.stats["total_latency_ms"] / self.stats["call_count"]
        
        return {
            **self.stats,
            "average_latency_ms": round(avg_latency, 2)
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.stats = {
            "friendli_calls": 0,
            "bedrock_calls": 0,
            "mock_calls": 0,
            "total_latency_ms": 0.0,
            "call_count": 0
        }
