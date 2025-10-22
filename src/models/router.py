"""
Model router with Friendli.ai as primary and AWS Bedrock as fallback.
"""
import os
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger(__name__)

try:
    import friendli
    FRIENDLI_AVAILABLE = True
except ImportError:
    FRIENDLI_AVAILABLE = False

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


@dataclass
class ModelResponse:
    """Response from a model with metadata."""
    text: str
    provider: str
    latency_ms: float
    model: str


class ModelRouter:
    """Routes requests to Friendli.ai or Bedrock with fallback."""
    
    def __init__(self):
        self.friendli_token = os.getenv("FRIENDLI_TOKEN")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
        
        # Statistics tracking
        self.stats = {
            "call_count": 0,
            "friendli_calls": 0,
            "bedrock_calls": 0,
            "mock_calls": 0,
            "total_latency_ms": 0.0
        }
        
        # Initialize Friendli client if available
        self.friendli_client = None
        if FRIENDLI_AVAILABLE and self.friendli_token:
            try:
                friendli.api_key = self.friendli_token
                self.friendli_client = friendli
            except Exception as e:
                logger.warning(f"Failed to initialize Friendli client: {e}")
        
        # Initialize Bedrock client if available
        self.bedrock_client = None
        if BOTO3_AVAILABLE:
            try:
                self.bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.bedrock_region
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock client: {e}")
    
    def llm_complete(
        self,
        prompt: str,
        model_hint: str = "general",
        max_tokens: int = 768,
        turbo_env: str = "USE_FRIENDLI"
    ) -> Dict[str, Any]:
        """
        Complete a prompt using available LLM provider with fallback.
        
        Args:
            prompt: The user prompt
            model_hint: Hint for model selection (e.g., "general", "fast", "quality")
            max_tokens: Maximum tokens to generate
            turbo_env: Environment variable to check for Friendli usage
            
        Returns:
            Dictionary with keys: text, provider, latency_ms
        """
        response = self.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return {
            "text": response.text,
            "provider": response.provider.lower(),
            "latency_ms": int(response.latency_ms)
        }
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        prefer_provider: Optional[str] = None
    ) -> ModelResponse:
        """
        Generate text using available LLM provider.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            prefer_provider: Prefer 'friendli' or 'bedrock' if available
            
        Returns:
            ModelResponse with generated text and metadata
        """
        self.stats["call_count"] += 1
        
        # Check USE_FRIENDLI environment variable
        use_friendli = os.getenv("USE_FRIENDLI", "1") == "1"
        
        providers = []
        if use_friendli and prefer_provider == "friendli" and self.friendli_client:
            providers = ["friendli", "bedrock"]
        elif prefer_provider == "bedrock" and self.bedrock_client:
            providers = ["bedrock", "friendli"] if use_friendli else ["bedrock"]
        else:
            # Default: try Friendli first (if enabled), then Bedrock
            if use_friendli:
                providers = ["friendli", "bedrock"]
            else:
                providers = ["bedrock"]
        
        last_error = None
        
        for provider in providers:
            try:
                if provider == "friendli" and self.friendli_client:
                    response = self._generate_friendli(
                        prompt, system_prompt, max_tokens, temperature
                    )
                    self.stats["friendli_calls"] += 1
                    self.stats["total_latency_ms"] += response.latency_ms
                    return response
                elif provider == "bedrock" and self.bedrock_client:
                    response = self._generate_bedrock(
                        prompt, system_prompt, max_tokens, temperature
                    )
                    self.stats["bedrock_calls"] += 1
                    self.stats["total_latency_ms"] += response.latency_ms
                    return response
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider} failed: {str(e)}")
                continue
        
        # If all providers fail, return mock response
        self.stats["mock_calls"] += 1
        logger.info("All providers failed, returning mock response")
        return ModelResponse(
            text="I apologize, but I'm unable to connect to the LLM providers at the moment. Please check your API credentials.",
            provider="mock",
            latency_ms=0,
            model="mock"
        )
    
    def _generate_friendli(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> ModelResponse:
        """Generate using Friendli.ai API."""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Use Friendli API
        response = friendli.ChatCompletion.create(
            model="meta-llama-3.1-70b-instruct",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return ModelResponse(
            text=response.choices[0].message.content,
            provider="Friendli.ai",
            latency_ms=round(latency_ms, 2),
            model="meta-llama-3.1-70b-instruct"
        )
    
    def _generate_bedrock(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> ModelResponse:
        """Generate using AWS Bedrock."""
        import json
        
        start_time = time.time()
        
        # Prepare prompt for Claude 3
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": full_prompt}
            ]
        })
        
        response = self.bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        latency_ms = (time.time() - start_time) * 1000
        
        return ModelResponse(
            text=response_body['content'][0]['text'],
            provider="AWS Bedrock",
            latency_ms=round(latency_ms, 2),
            model="Claude 3 Sonnet"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics.
        
        Returns:
            Dictionary with call counts and average latency
        """
        avg_latency = 0.0
        if self.stats["call_count"] > 0:
            avg_latency = self.stats["total_latency_ms"] / self.stats["call_count"]
        
        return {
            "call_count": self.stats["call_count"],
            "friendli_calls": self.stats["friendli_calls"],
            "bedrock_calls": self.stats["bedrock_calls"],
            "mock_calls": self.stats["mock_calls"],
            "average_latency_ms": round(avg_latency, 2)
        }
