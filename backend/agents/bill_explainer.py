"""
Bill Explainer Agent - Enhanced with cost data analysis.
"""
from typing import Dict, Any, Optional
from backend.utils.model_router import ModelRouter, LLMResponse
from backend.utils.aws_clients import AWSClients
from backend.utils.weaviate_client import WeaviateClient


class BillExplainerAgent:
    """Agent specialized in AWS billing analysis and explanation."""
    
    def __init__(
        self,
        model_router: ModelRouter,
        aws_clients: Optional[AWSClients] = None,
        weaviate_client: Optional[WeaviateClient] = None
    ):
        self.model_router = model_router
        self.aws_clients = aws_clients or AWSClients()
        self.weaviate_client = weaviate_client
        self.name = "Bill Explainer"
    
    def get_system_prompt(self) -> str:
        return """You are Bill Explainer, an AWS billing and cost analysis expert. Your role is to:

1. Break down AWS bills into understandable components
2. Explain pricing models for various AWS services
3. Identify the main cost drivers
4. Help users understand unexpected charges
5. Provide context about typical AWS costs
6. Explain the difference between various charge types (usage, data transfer, storage, etc.)

Always be empathetic and clear. Use simple language to explain complex billing concepts.
When analyzing costs, focus on actionable insights and help users understand what they're paying for."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process billing-related queries."""
        
        # Get cost data
        cost_data = self.aws_clients.get_cost_data()
        cost_context = self._format_cost_data(cost_data)
        
        # Search for relevant documentation
        relevant_docs = ""
        if self.weaviate_client and self.weaviate_client.is_available():
            docs = self.weaviate_client.hybrid_search(
                collection_name="AWSDocs",
                query=f"{user_input} pricing billing",
                limit=3
            )
            if docs:
                relevant_docs = "\n\nRelevant Pricing Documentation:\n"
                for i, doc in enumerate(docs, 1):
                    relevant_docs += f"\n{i}. {doc.get('title', 'AWS Docs')}\n"
                    relevant_docs += f"   {doc.get('content', '')[:200]}...\n"
        
        # Build prompt
        prompt = f"{user_input}\n\n{cost_context}{relevant_docs}"
        if context:
            prompt += self._format_context(context)
        
        # Generate response
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.6
        )
        
        return response
    
    def explain_bill(self) -> LLMResponse:
        """Explain the current AWS bill."""
        cost_data = self.aws_clients.get_cost_data()
        
        prompt = f"""Explain this AWS bill in simple terms:

{self._format_cost_data(cost_data)}

Provide:
1. A summary of total costs
2. Top 3 cost drivers
3. Any unusual patterns or spikes
4. Simple explanations of what each major service does"""
        
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1200,
            temperature=0.7
        )
        
        return response
    
    def _format_cost_data(self, cost_data: Dict[str, Any]) -> str:
        """Format cost data into readable string."""
        formatted = f"Current AWS Costs:\n"
        formatted += f"Total: ${cost_data.get('total_cost', 0):.2f}\n\n"
        formatted += "Breakdown by Service:\n"
        
        services = cost_data.get('cost_by_service', {})
        sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
        
        for service, cost in sorted_services[:10]:  # Top 10 services
            percentage = (cost / cost_data.get('total_cost', 1)) * 100
            formatted += f"  - {service}: ${cost:.2f} ({percentage:.1f}%)\n"
        
        period = cost_data.get('period', {})
        formatted += f"\nPeriod: {period.get('start', 'N/A')} to {period.get('end', 'N/A')}\n"
        
        return formatted
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into a string."""
        if not context:
            return ""
        
        formatted = "\n\nAdditional Context:\n"
        for key, value in context.items():
            formatted += f"- {key}: {value}\n"
        return formatted
