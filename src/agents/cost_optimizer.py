"""
Cost Optimizer Agent - Helps users optimize AWS costs.
"""
from typing import Dict, Any, Optional, List
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class CostOptimizerAgent(BaseAgent):
    """Agent specialized in AWS cost optimization."""
    
    def get_system_prompt(self) -> str:
        return """You are Cost Optimizer, an expert at helping users reduce AWS costs. Your role is to:

1. Identify cost optimization opportunities
2. Recommend specific actions to reduce spending
3. Explain trade-offs between cost and performance
4. Suggest right-sizing for over-provisioned resources
5. Recommend Reserved Instances, Savings Plans, and Spot Instances
6. Identify unused or underutilized resources

Be specific, actionable, and data-driven. Quantify savings whenever possible. Consider both short-term and long-term optimizations."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process cost optimization queries."""
        
        # Add context (including cost data if available)
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
    
    def analyze_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost data and generate optimization recommendations."""
        prompt = f"""Analyze this AWS cost data and provide optimization recommendations:

{self._format_cost_data(cost_data)}

Provide:
1. Top 3-5 optimization opportunities
2. Estimated monthly savings for each
3. Implementation difficulty (Easy/Medium/Hard)
4. Specific action items"""
        
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.5
        )
        
        # Parse recommendations and calculate total potential savings
        recommendations = self._parse_recommendations(response.text)
        
        return {
            "recommendations": recommendations,
            "analysis": response.text,
            "total_potential_savings": sum(r.get("savings", 0) for r in recommendations)
        }
    
    def _format_cost_data(self, cost_data: Dict[str, Any]) -> str:
        """Format cost data for LLM consumption."""
        formatted = ""
        if "current_cost" in cost_data:
            formatted += f"Current Monthly Cost: ${cost_data['current_cost']:.2f}\n"
        if "resources" in cost_data:
            formatted += "\nResources:\n"
            for resource in cost_data["resources"]:
                formatted += f"  - {resource.get('type', 'Unknown')}: {resource.get('name', 'N/A')}\n"
                formatted += f"    Cost: ${resource.get('cost', 0):.2f}/month\n"
                if "utilization" in resource:
                    formatted += f"    Utilization: {resource['utilization']}%\n"
        return formatted
    
    def _parse_recommendations(self, text: str) -> List[Dict[str, Any]]:
        """Parse recommendations from LLM response."""
        # Simple parsing - in production, this would be more sophisticated
        recommendations = []
        
        # For now, return a basic structure
        # In a real implementation, this would parse the LLM output
        recommendations.append({
            "title": "Optimization recommendations generated",
            "savings": 0,
            "difficulty": "Medium"
        })
        
        return recommendations
