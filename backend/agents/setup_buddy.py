"""
Setup Buddy Agent - Enhanced with tools for CloudFormation and Excalidraw.
"""
from typing import Dict, Any, Optional
from backend.utils.model_router import ModelRouter, LLMResponse
from backend.utils.weaviate_client import WeaviateClient


class SetupBuddyAgent:
    """Agent specialized in AWS infrastructure setup and deployment."""
    
    def __init__(
        self,
        model_router: ModelRouter,
        weaviate_client: Optional[WeaviateClient] = None
    ):
        self.model_router = model_router
        self.weaviate_client = weaviate_client
        self.name = "Setup Buddy"
    
    def get_system_prompt(self) -> str:
        return """You are Setup Buddy, an expert AWS infrastructure consultant. Your role is to:

1. Help users design and deploy AWS infrastructure
2. Generate CloudFormation templates for common patterns
3. Provide best practices for security, scalability, and cost optimization
4. Guide users through the setup process step by step
5. Explain AWS services in simple terms
6. Create architecture diagrams to visualize infrastructure

Always be friendly, clear, and practical. Focus on helping users get their infrastructure up and running quickly and correctly.
When providing CloudFormation templates, use YAML format and include proper resource naming, dependencies, and outputs."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process setup-related queries."""
        
        # Search for relevant documentation if Weaviate is available
        relevant_docs = ""
        if self.weaviate_client and self.weaviate_client.is_available():
            docs = self.weaviate_client.hybrid_search(
                collection_name="AWSDocs",
                query=user_input,
                limit=3
            )
            if docs:
                relevant_docs = "\n\nRelevant AWS Documentation:\n"
                for i, doc in enumerate(docs, 1):
                    relevant_docs += f"\n{i}. {doc.get('title', 'AWS Docs')}\n"
                    relevant_docs += f"   {doc.get('content', '')[:300]}...\n"
        
        # Build prompt with context
        prompt = user_input + relevant_docs
        if context:
            prompt += self._format_context(context)
        
        # Generate response using model router
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.7
        )
        
        return response
    
    def generate_cloudformation(self, infrastructure_desc: str) -> LLMResponse:
        """Generate CloudFormation template based on description."""
        prompt = f"""Generate a CloudFormation template in YAML format for the following infrastructure:

{infrastructure_desc}

Include:
- Proper resource naming and logical IDs
- Resource dependencies using DependsOn where needed
- Security best practices (security groups, IAM roles, encryption)
- Outputs for important resource IDs and endpoints
- Comments explaining key sections
- Parameters for customization where appropriate

Follow AWS CloudFormation best practices and make the template production-ready."""
        
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=2000,
            temperature=0.3
        )
        
        return response
    
    def generate_diagram_description(self, infrastructure_desc: str) -> str:
        """Generate a description for creating an Excalidraw diagram."""
        prompt = f"""Based on this infrastructure description:

{infrastructure_desc}

List the AWS resources and their connections that should be shown in an architecture diagram.
Format as:
- Resource1 (type): description
- Resource2 (type): description
- Connection: Resource1 → Resource2 (purpose)

Be concise and focus on the key components."""
        
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=800,
            temperature=0.5
        )
        
        return response.text
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into a string."""
        if not context:
            return ""
        
        formatted = "\n\nAdditional Context:\n"
        for key, value in context.items():
            formatted += f"- {key}: {value}\n"
        return formatted
