"""
Cost Optimizer Agent - Enhanced with AWS resource analysis.
"""
from typing import Dict, Any, Optional, List
from backend.utils.model_router import ModelRouter, LLMResponse
from backend.utils.aws_clients import AWSClients


class CostOptimizerAgent:
    """Agent specialized in AWS cost optimization."""
    
    def __init__(
        self,
        model_router: ModelRouter,
        aws_clients: Optional[AWSClients] = None
    ):
        self.model_router = model_router
        self.aws_clients = aws_clients or AWSClients()
        self.name = "Cost Optimizer"
    
    def get_system_prompt(self) -> str:
        return """You are Cost Optimizer, an AWS cost optimization expert. Your role is to:

1. Identify specific opportunities to reduce AWS costs
2. Quantify potential savings for each optimization
3. Provide actionable, step-by-step recommendations
4. Prioritize optimizations by impact and ease of implementation
5. Explain the risks and benefits of each optimization
6. Help users understand AWS pricing models to avoid waste

Be specific with numbers and recommendations. Focus on practical optimizations that users can implement quickly.
Always explain why each optimization will save money and any potential trade-offs."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process cost optimization queries."""
        
        # Gather optimization data
        idle_instances = self.aws_clients.list_idle_ec2_instances()
        old_snapshots = self.aws_clients.list_old_snapshots()
        s3_opportunities = self.aws_clients.analyze_s3_lifecycle_opportunities()
        cost_data = self.aws_clients.get_cost_data()
        
        # Format optimization context
        optimization_context = self._format_optimization_data(
            idle_instances, old_snapshots, s3_opportunities, cost_data
        )
        
        # Build prompt
        prompt = f"{user_input}\n\n{optimization_context}"
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
    
    def analyze_optimizations(self) -> LLMResponse:
        """Analyze and provide comprehensive cost optimization recommendations."""
        
        # Gather all optimization data
        idle_instances = self.aws_clients.list_idle_ec2_instances()
        old_snapshots = self.aws_clients.list_old_snapshots()
        s3_opportunities = self.aws_clients.analyze_s3_lifecycle_opportunities()
        cost_data = self.aws_clients.get_cost_data()
        
        # Calculate total savings
        ec2_savings = sum(inst.get('monthly_cost', 0) for inst in idle_instances)
        snapshot_savings = sum(snap.get('monthly_cost', 0) for snap in old_snapshots)
        s3_savings = sum(opp.get('estimated_savings', 0) for opp in s3_opportunities)
        total_savings = ec2_savings + snapshot_savings + s3_savings
        
        prompt = f"""Analyze these cost optimization opportunities and provide specific recommendations:

{self._format_optimization_data(idle_instances, old_snapshots, s3_opportunities, cost_data)}

Total Potential Monthly Savings: ${total_savings:.2f}

For each category:
1. Prioritize by impact (savings amount)
2. Provide step-by-step instructions to implement
3. Mention any risks or considerations
4. Estimate implementation time

Format your response clearly with sections for each optimization type."""
        
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=2000,
            temperature=0.5
        )
        
        return response
    
    def _format_optimization_data(
        self,
        idle_instances: List[Dict],
        old_snapshots: List[Dict],
        s3_opportunities: List[Dict],
        cost_data: Dict
    ) -> str:
        """Format optimization data into readable string."""
        formatted = "Current AWS Environment Analysis:\n\n"
        
        # Cost summary
        formatted += f"Total Monthly Cost: ${cost_data.get('total_cost', 0):.2f}\n\n"
        
        # Idle EC2 instances
        if idle_instances:
            ec2_savings = sum(inst.get('monthly_cost', 0) for inst in idle_instances)
            formatted += f"1. IDLE EC2 INSTANCES ({len(idle_instances)} found)\n"
            formatted += f"   Potential savings: ${ec2_savings:.2f}/month\n"
            for inst in idle_instances[:5]:  # Show top 5
                formatted += f"   - {inst['instance_id']} ({inst['instance_type']}): "
                formatted += f"CPU {inst.get('cpu_utilization', 0):.1f}% → ${inst.get('monthly_cost', 0):.2f}/mo\n"
            if len(idle_instances) > 5:
                formatted += f"   ... and {len(idle_instances) - 5} more\n"
            formatted += "\n"
        
        # Old snapshots
        if old_snapshots:
            snapshot_savings = sum(snap.get('monthly_cost', 0) for snap in old_snapshots)
            total_size = sum(snap.get('volume_size', 0) for snap in old_snapshots)
            formatted += f"2. OLD EBS SNAPSHOTS ({len(old_snapshots)} found)\n"
            formatted += f"   Total size: {total_size} GB\n"
            formatted += f"   Potential savings: ${snapshot_savings:.2f}/month\n"
            for snap in old_snapshots[:3]:
                formatted += f"   - {snap['snapshot_id']}: {snap.get('volume_size', 0)} GB, "
                formatted += f"created {snap.get('start_time', 'N/A')}\n"
            formatted += "\n"
        
        # S3 opportunities
        if s3_opportunities:
            s3_savings = sum(opp.get('estimated_savings', 0) for opp in s3_opportunities)
            formatted += f"3. S3 LIFECYCLE OPPORTUNITIES ({len(s3_opportunities)} found)\n"
            formatted += f"   Potential savings: ${s3_savings:.2f}/month\n"
            for opp in s3_opportunities:
                formatted += f"   - {opp['bucket_name']}: {opp['recommendation']}\n"
            formatted += "\n"
        
        # Total
        total = (sum(inst.get('monthly_cost', 0) for inst in idle_instances) +
                 sum(snap.get('monthly_cost', 0) for snap in old_snapshots) +
                 sum(opp.get('estimated_savings', 0) for opp in s3_opportunities))
        formatted += f"TOTAL POTENTIAL SAVINGS: ${total:.2f}/month (${total * 12:.2f}/year)\n"
        
        return formatted
    
    def get_savings_summary(self) -> Dict[str, Any]:
        """Get a summary of potential savings."""
        idle_instances = self.aws_clients.list_idle_ec2_instances()
        old_snapshots = self.aws_clients.list_old_snapshots()
        s3_opportunities = self.aws_clients.analyze_s3_lifecycle_opportunities()
        
        ec2_savings = sum(inst.get('monthly_cost', 0) for inst in idle_instances)
        snapshot_savings = sum(snap.get('monthly_cost', 0) for snap in old_snapshots)
        s3_savings = sum(opp.get('estimated_savings', 0) for opp in s3_opportunities)
        
        return {
            'ec2_idle_instances': {
                'count': len(idle_instances),
                'monthly_savings': ec2_savings
            },
            'old_snapshots': {
                'count': len(old_snapshots),
                'monthly_savings': snapshot_savings
            },
            's3_lifecycle': {
                'count': len(s3_opportunities),
                'monthly_savings': s3_savings
            },
            'total_monthly_savings': ec2_savings + snapshot_savings + s3_savings,
            'total_annual_savings': (ec2_savings + snapshot_savings + s3_savings) * 12
        }
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into a string."""
        if not context:
            return ""
        
        formatted = "\n\nAdditional Context:\n"
        for key, value in context.items():
            formatted += f"- {key}: {value}\n"
        return formatted
