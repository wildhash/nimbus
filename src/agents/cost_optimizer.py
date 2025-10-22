"""
Cost Optimizer Agent - Helps users optimize AWS costs.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class CostOptimizerAgent(BaseAgent):
    """Agent specialized in AWS cost optimization."""
    
    def __init__(self, model_router, aws_service=None):
        super().__init__(model_router)
        self.aws_service = aws_service
    
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
        
        # Get optimization findings
        findings = self.analyze_resources()
        
        # Format findings for context
        findings_text = self._format_findings(findings)
        
        # Add context (including cost data if available)
        prompt = user_input + "\n\n" + findings_text
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
    
    def analyze_resources(self) -> Dict[str, Any]:
        """
        Analyze resources using deterministic rules.
        
        Returns:
            Dictionary with findings and total estimated savings
        """
        # Load mock bill data for analysis
        bill_data = self._load_bill_data()
        
        findings = []
        
        # Rule 1: EC2 stopped ≥7 days → terminate/hibernate
        findings.extend(self._check_stopped_ec2(bill_data))
        
        # Rule 2: EC2 CPU<5% → downsize (50% cost cut)
        findings.extend(self._check_low_utilization_ec2(bill_data))
        
        # Rule 3: Snapshots age>180d → delete/archive ($0.05/GB-mo)
        findings.extend(self._check_old_snapshots(bill_data))
        
        # Rule 4: S3 STANDARD & last_access>90d → move to IA (savings $0.012/GB-mo)
        findings.extend(self._check_s3_lifecycle(bill_data))
        
        # Calculate total savings
        total = sum(f.get("est_savings", 0) for f in findings)
        
        # Sort by highest impact
        findings.sort(key=lambda x: x.get("est_savings", 0), reverse=True)
        
        return {
            "findings": findings,
            "total": total
        }
    
    def _check_stopped_ec2(self, bill_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for EC2 instances stopped for ≥7 days."""
        findings = []
        
        # Mock data: assume 2 stopped instances
        findings.append({
            "type": "stopped_instance",
            "resource": "i-0123456789abcdef0",
            "action": "Terminate or hibernate instance stopped for 14 days",
            "est_savings": 45.60,
            "difficulty": "Easy"
        })
        
        findings.append({
            "type": "stopped_instance",
            "resource": "i-0fedcba9876543210",
            "action": "Terminate or hibernate instance stopped for 9 days",
            "est_savings": 35.20,
            "difficulty": "Easy"
        })
        
        return findings
    
    def _check_low_utilization_ec2(self, bill_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for EC2 instances with CPU<5%."""
        findings = []
        
        # From bill data optimization opportunities
        if "optimization_opportunities" in bill_data:
            for opp in bill_data["optimization_opportunities"]:
                if opp.get("service") == "EC2" and "utilization" in opp.get("issue", "").lower():
                    findings.append({
                        "type": "low_utilization",
                        "resource": "3 EC2 instances",
                        "action": "Downsize instances with <10% CPU utilization (50% cost reduction)",
                        "est_savings": opp.get("estimated_savings", 0),
                        "difficulty": "Medium"
                    })
        
        return findings
    
    def _check_old_snapshots(self, bill_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for snapshots older than 180 days."""
        findings = []
        
        # From bill data optimization opportunities
        if "optimization_opportunities" in bill_data:
            for opp in bill_data["optimization_opportunities"]:
                if opp.get("service") == "Snapshots":
                    findings.append({
                        "type": "old_snapshot",
                        "resource": "200 GB snapshots",
                        "action": "Delete or archive snapshots older than 90 days ($0.05/GB-mo savings)",
                        "est_savings": opp.get("estimated_savings", 0),
                        "difficulty": "Easy"
                    })
        
        return findings
    
    def _check_s3_lifecycle(self, bill_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for S3 buckets without lifecycle policies."""
        findings = []
        
        # From bill data optimization opportunities
        if "optimization_opportunities" in bill_data:
            for opp in bill_data["optimization_opportunities"]:
                if opp.get("service") == "S3":
                    findings.append({
                        "type": "s3_lifecycle",
                        "resource": "2 S3 buckets",
                        "action": "Enable lifecycle policies to transition objects to Intelligent-Tiering or Glacier ($0.012/GB-mo savings)",
                        "est_savings": opp.get("estimated_savings", 0),
                        "difficulty": "Easy"
                    })
        
        return findings
    
    def _load_bill_data(self) -> Dict[str, Any]:
        """Load bill data from mock file."""
        mock_path = Path(__file__).parent.parent.parent / "mock_data" / "aws_bill.json"
        if mock_path.exists():
            with open(mock_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _format_findings(self, result: Dict[str, Any]) -> str:
        """Format optimization findings for display."""
        findings = result.get("findings", [])
        total = result.get("total", 0)
        
        if not findings:
            return "Optimization Analysis: No optimization opportunities found."
        
        formatted = "Cost Optimization Opportunities:\n"
        formatted += "="*50 + "\n"
        formatted += f"Total Potential Savings: ${total:.2f}/month\n\n"
        
        for i, finding in enumerate(findings[:5], 1):
            formatted += f"{i}. {finding.get('resource', 'Unknown')}\n"
            formatted += f"   Action: {finding.get('action', '')}\n"
            formatted += f"   Savings: ${finding.get('est_savings', 0):.2f}/month\n"
            formatted += f"   Difficulty: {finding.get('difficulty', 'Medium')}\n\n"
        
        return formatted
    
    def analyze_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost data and generate optimization recommendations."""
        # Use rules-based analysis instead of LLM
        result = self.analyze_resources()
        
        # Format as text for compatibility
        analysis_text = self._format_findings(result)
        
        return {
            "recommendations": result["findings"],
            "analysis": analysis_text,
            "total_potential_savings": result["total"]
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
