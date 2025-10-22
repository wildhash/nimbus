"""
AWS Bedrock client wrapper for LLM inference.
"""
import os
import json
import time
from typing import Optional, List, Dict, Any

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class BedrockClient:
    """Client for AWS Bedrock API."""
    
    def __init__(self):
        self.region = os.getenv("BEDROCK_REGION", "us-east-1")
        self.default_model = os.getenv("BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
        
        self.client = None
        if BOTO3_AVAILABLE:
            try:
                self.client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Bedrock client: {e}")
    
    def is_available(self) -> bool:
        """Check if Bedrock client is available."""
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
        Generate completion using AWS Bedrock.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Model to use (defaults to Claude 3 Sonnet)
            
        Returns:
            Dictionary with text, latency_ms, and metadata
        """
        if not self.client:
            raise Exception("Bedrock client not initialized")
        
        start_time = time.time()
        model_id = model or self.default_model
        
        # Build messages for Claude
        messages = []
        full_prompt = prompt
        
        if system_prompt:
            # Claude 3 supports system prompts in the messages array
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        messages.append({"role": "user", "content": full_prompt})
        
        try:
            # Prepare request body for Claude 3
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            })
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "text": response_body['content'][0]['text'],
                "latency_ms": round(latency_ms, 2),
                "model": model_id,
                "provider": "AWS Bedrock",
                "success": True
            }
        except Exception as e:
            raise Exception(f"Bedrock API error: {str(e)}")
    
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
            raise Exception("Bedrock client not initialized")
        
        start_time = time.time()
        model_id = model or self.default_model
        
        # Convert messages to Claude format
        # Extract system message if present
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        try:
            # Prepare request body
            body_dict = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": user_messages if user_messages else messages
            }
            
            if system_message:
                # For multi-turn, prepend system to first user message
                if body_dict["messages"] and body_dict["messages"][0]["role"] == "user":
                    body_dict["messages"][0]["content"] = f"{system_message}\n\n{body_dict['messages'][0]['content']}"
            
            body = json.dumps(body_dict)
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "text": response_body['content'][0]['text'],
                "latency_ms": round(latency_ms, 2),
                "model": model_id,
                "provider": "AWS Bedrock",
                "success": True
            }
        except Exception as e:
            raise Exception(f"Bedrock API error: {str(e)}")
