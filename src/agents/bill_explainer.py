"""
Bill Explainer Agent - Helps users understand their AWS bills.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class BillExplainerAgent(BaseAgent):
    """Agent specialized in explaining AWS bills and costs."""
    
    def __init__(self, model_router, aws_service=None):
        super().__init__(model_router)
        self.aws_service = aws_service
    
    def get_system_prompt(self) -> str:
        return """You are Bill Explainer, an expert at helping users understand their AWS bills. Your role is to:

1. Break down AWS bills into understandable components
2. Explain AWS pricing models and cost structures
3. Identify the largest cost drivers in a bill
4. Clarify confusing line items and charges
5. Help users understand usage patterns and trends
6. Detect anomalies and unusual spending patterns

Be clear, patient, and thorough. Use analogies when helpful. Focus on making complex billing information accessible."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process bill-related queries."""
        
        # Load bill data (mock or live)
        bill_data = self._load_bill_data()
        
        # Detect anomalies
        anomalies = self._detect_anomalies(bill_data)
        
        # Format bill information
        bill_summary = self._format_bill_summary(bill_data, anomalies)
        
        # Add context (including bill data if available)
        prompt = user_input + "\n\n" + bill_summary
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
    
    def _load_bill_data(self) -> Dict[str, Any]:
        """Load bill data from mock file or AWS Cost Explorer."""
        # Try live AWS data first if service is available
        if self.aws_service and hasattr(self.aws_service, 'get_cost_data'):
            try:
                return self.aws_service.get_cost_data()
            except Exception as e:
                print(f"Failed to get live cost data: {e}, falling back to mock")
        
        # Fall back to mock data
        mock_path = Path(__file__).parent.parent.parent / "mock_data" / "aws_bill.json"
        if mock_path.exists():
            with open(mock_path, 'r') as f:
                return json.load(f)
        
        return {}
    
    def _detect_anomalies(self, bill_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Detect anomalies in bill data using heuristics.
        
        Args:
            bill_data: Bill data dictionary
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        
        if not bill_data or "services" not in bill_data:
            return anomalies
        
        # Calculate service costs
        service_costs = {}
        if isinstance(bill_data["services"], list):
            for service in bill_data["services"]:
                name = service.get("service_name", "Unknown")
                cost = service.get("cost", 0)
                service_costs[name] = cost
        else:
            service_costs = bill_data["services"]
        
        total_cost = bill_data.get("total_cost", sum(service_costs.values()))
        
        # Anomaly 1: Data Transfer spike (>10% of total)
        data_transfer_cost = service_costs.get("AWS Data Transfer", 0)
        if data_transfer_cost > 0 and total_cost > 0:
            data_transfer_pct = (data_transfer_cost / total_cost) * 100
            if data_transfer_pct > 10:
                anomalies.append({
                    "type": "cost_spike",
                    "service": "AWS Data Transfer",
                    "description": f"Data Transfer costs are {data_transfer_pct:.1f}% of total bill (${data_transfer_cost:.2f})",
                    "hypothesis": "Possible causes: increased cross-region traffic, public data egress, or CloudFront misconfig"
                })
        
        # Anomaly 2: High compute cost with low utilization indicators
        ec2_cost = service_costs.get("Amazon Elastic Compute Cloud", 0)
        if ec2_cost > total_cost * 0.3:
            anomalies.append({
                "type": "high_compute",
                "service": "Amazon Elastic Compute Cloud",
                "description": f"EC2 represents {(ec2_cost/total_cost)*100:.1f}% of costs (${ec2_cost:.2f})",
                "hypothesis": "Review optimization opportunities in bill - may have idle or underutilized instances"
            })
        
        # Anomaly 3: Check optimization opportunities from bill data
        if "optimization_opportunities" in bill_data:
            for opp in bill_data["optimization_opportunities"]:
                anomalies.append({
                    "type": "optimization",
                    "service": opp.get("service", "Unknown"),
                    "description": opp.get("issue", ""),
                    "hypothesis": opp.get("recommendation", "")
                })
        
        return anomalies
    
    def _format_bill_summary(
        self,
        bill_data: Dict[str, Any],
        anomalies: List[Dict[str, str]]
    ) -> str:
        """Format bill data and anomalies for LLM consumption."""
        if not bill_data:
            return "Current Bill Information: No bill data available"
        
        formatted = "Current Bill Information:\n"
        formatted += "="*50 + "\n"
        
        # Total cost
        total = bill_data.get("total_cost", 0)
        formatted += f"Total Cost: ${total:.2f}\n"
        
        # Billing period
        if "billing_period" in bill_data:
            period = bill_data["billing_period"]
            formatted += f"Period: {period.get('start')} to {period.get('end')}\n"
        
        formatted += "\n"
        
        # Top services
        formatted += "Top Services by Cost:\n"
        service_costs = []
        
        if isinstance(bill_data.get("services", []), list):
            for service in bill_data["services"][:5]:
                name = service.get("service_name", "Unknown")
                cost = service.get("cost", 0)
                pct = (cost / total * 100) if total > 0 else 0
                service_costs.append((name, cost, pct))
        
        for name, cost, pct in service_costs:
            formatted += f"  • {name}: ${cost:.2f} ({pct:.1f}%)\n"
        
        # Anomalies
        if anomalies:
            formatted += "\nDetected Anomalies:\n"
            for i, anomaly in enumerate(anomalies[:3], 1):
                formatted += f"\n{i}. {anomaly.get('service', 'Unknown')}: {anomaly.get('description', '')}\n"
                formatted += f"   Hypothesis: {anomaly.get('hypothesis', '')}\n"
        
        return formatted
    
    def analyze_bill(self, bill_data: Dict[str, Any]) -> str:
        """Analyze bill data and provide insights."""
        anomalies = self._detect_anomalies(bill_data)
        
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
            if isinstance(bill_data["services"], list):
                for service in bill_data["services"]:
                    name = service.get("service_name", "Unknown")
                    cost = service.get("cost", 0)
                    formatted += f"  - {name}: ${cost:.2f}\n"
            else:
                for service, cost in bill_data["services"].items():
                    formatted += f"  - {service}: ${cost:.2f}\n"
        if "billing_period" in bill_data:
            period = bill_data["billing_period"]
            formatted += f"\nBilling Period: {period.get('start')} to {period.get('end')}\n"
        return formatted
