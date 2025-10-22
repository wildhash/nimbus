"""
LLM provider implementations for Friendli.ai and AWS Bedrock.
"""
import os
import time
import json
import logging
from typing import Optional, Dict, Any

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


def friendli_complete(
    prompt: str,
    max_tokens: int = 768,
    model_id: str = "llama-3.1-70b-instruct",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Complete a prompt using Friendli.ai API.
    
    Args:
        prompt: User prompt
        max_tokens: Maximum tokens to generate
        model_id: Model identifier
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        
    Returns:
        Generated text
        
    Raises:
        Exception: If Friendli API call fails
    """
    if not FRIENDLI_AVAILABLE:
        raise ImportError("friendli package not available")
    
    friendli_token = os.getenv("FRIENDLI_TOKEN")
    if not friendli_token:
        raise ValueError("FRIENDLI_TOKEN environment variable not set")
    
    # Set API key
    friendli.api_key = friendli_token
    
    # Prepare messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Make API call
    response = friendli.ChatCompletion.create(
        model=model_id,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return response.choices[0].message.content


def bedrock_complete(
    prompt: str,
    max_tokens: int = 768,
    model_hint: str = "general",
    system_prompt: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Complete a prompt using AWS Bedrock API.
    
    Args:
        prompt: User prompt
        max_tokens: Maximum tokens to generate
        model_hint: Hint for model selection
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        
    Returns:
        Generated text
        
    Raises:
        Exception: If Bedrock API call fails
    """
    if not BOTO3_AVAILABLE:
        raise ImportError("boto3 package not available")
    
    bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
    
    # Initialize Bedrock client
    client = boto3.client(
        service_name='bedrock-runtime',
        region_name=bedrock_region
    )
    
    # Prepare prompt for Claude 3
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"
    
    # Prepare request body
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": full_prompt}
        ]
    })
    
    # Make API call
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']
