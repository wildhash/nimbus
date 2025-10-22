"""
Bill Explainer Agent - Helps users understand their AWS bills.
"""
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class BillExplainerAgent(BaseAgent):
    """Agent specialized in explaining AWS bills and costs."""
    
    def get_system_prompt(self) -> str:
        return """You are Bill Explainer, an expert at helping users understand their AWS bills. Your role is to:

1. Break down AWS bills into understandable components
2. Explain AWS pricing models and cost structures
3. Identify the largest cost drivers in a bill
4. Clarify confusing line items and charges
5. Help users understand usage patterns and trends

Be clear, patient, and thorough. Use analogies when helpful. Focus on making complex billing information accessible."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process bill-related queries."""
        
        # Add context (including bill data if available)
        prompt = user_input
        if context:
            prompt += self.format_context(context)
        
        # Generate response
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.6
        )
        
        return response
    
    def analyze_bill(self, bill_data: Dict[str, Any]) -> str:
        """Analyze bill data and provide insights."""
        prompt = f"""Analyze this AWS bill data and provide insights:

{self._format_bill_data(bill_data)}

Provide:
1. Top 3 cost drivers
2. Key findings
3. Any unusual charges or patterns
4. Summary in simple terms"""
        
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1000,
            temperature=0.5
        )
        
        return response.text
    
    def _format_bill_data(self, bill_data: Dict[str, Any]) -> str:
        """Format bill data for LLM consumption."""
        formatted = ""
        if "total_cost" in bill_data:
            formatted += f"Total Cost: ${bill_data['total_cost']:.2f}\n"
        if "services" in bill_data:
            formatted += "\nCosts by Service:\n"
            for service, cost in bill_data["services"].items():
                formatted += f"  - {service}: ${cost:.2f}\n"
        if "period" in bill_data:
            formatted += f"\nBilling Period: {bill_data['period']}\n"
        return formatted
