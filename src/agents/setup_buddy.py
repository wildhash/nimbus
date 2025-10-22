"""
Setup Buddy Agent - Helps users set up AWS infrastructure.
"""
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class SetupBuddyAgent(BaseAgent):
    """Agent specialized in AWS infrastructure setup and deployment."""
    
    def get_system_prompt(self) -> str:
        return """You are Setup Buddy, an expert AWS infrastructure consultant. Your role is to:

1. Help users design and deploy AWS infrastructure
2. Generate CloudFormation templates for common patterns
3. Provide best practices for security, scalability, and cost optimization
4. Guide users through the setup process step by step
5. Explain AWS services in simple terms

Always be friendly, clear, and practical. Focus on helping users get their infrastructure up and running quickly and correctly."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process setup-related queries."""
        
        # Add context to the prompt
        prompt = user_input
        if context:
            prompt += self.format_context(context)
        
        # Generate response using model router
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.7
        )
        
        return response
    
    def generate_cloudformation(self, infrastructure_desc: str) -> str:
        """Generate CloudFormation template based on description."""
        prompt = f"""Generate a CloudFormation template in YAML format for the following infrastructure:

{infrastructure_desc}

Include proper resource naming, dependencies, and outputs. Follow AWS best practices."""
        
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.text
