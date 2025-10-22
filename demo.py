"""
Demo script showing Nimbus Copilot capabilities.
Run this to see example usage without starting the full Streamlit app.
"""
import os
import sys

# Set mock mode
os.environ['USE_MOCK_DATA'] = 'true'

from src.models.router import ModelRouter
from src.orchestrator import AgentOrchestrator
from src.services.aws_service import MockAWSService
from src.services.excalidraw_service import ExcalidrawService
from src.utils.cloudformation import CloudFormationGenerator


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def demo_orchestrator():
    """Demo the agent orchestrator."""
    print_header("🤖 Agent Orchestrator Demo")
    
    router = ModelRouter()
    orchestrator = AgentOrchestrator(router)
    
    queries = [
        "How do I create a VPC with public and private subnets?",
        "What is the difference between EC2 instance types?",
        "Why is my S3 bill so high this month?",
        "How can I reduce my EC2 costs?",
    ]
    
    for query in queries:
        print(f"Query: {query}")
        result = orchestrator.process_query(query)
        print(f"  → Agent: {result['agent_display']}")
        print(f"  → Provider: {result['provider']}")
        print(f"  → Latency: {result['latency_ms']:.0f}ms")
        print(f"  → Reasoning: {result['reasoning']}")
        print(f"  → Response: {result['response'][:200]}...\n")


def demo_cost_analysis():
    """Demo cost analysis features."""
    print_header("💰 Cost Analysis Demo")
    
    aws_service = MockAWSService()
    
    # Get cost breakdown
    cost_data = aws_service.get_cost_breakdown()
    print(f"Total Monthly Cost: ${cost_data['total_cost']:.2f}\n")
    
    print("Cost by Service:")
    for service, cost in list(cost_data['services'].items())[:5]:
        print(f"  {service}: ${cost:.2f}")
    
    print("\nTop Resources:")
    for resource in cost_data['resources'][:3]:
        print(f"  {resource['type']}/{resource['name']}: ${resource['cost']:.2f}")
        print(f"    Utilization: {resource['utilization']}%")
    
    # Get optimization opportunities
    print("\n💡 Optimization Opportunities:")
    opportunities = aws_service.get_optimization_opportunities()
    total_savings = sum(opp['estimated_savings'] for opp in opportunities)
    
    for opp in opportunities[:3]:
        print(f"\n  • {opp['title']}")
        print(f"    Savings: ${opp['estimated_savings']:.2f}/month")
        print(f"    Difficulty: {opp['difficulty']}")
        print(f"    Action: {opp['action']}")
    
    print(f"\nTotal Potential Savings: ${total_savings:.2f}/month")


def demo_cloudformation():
    """Demo CloudFormation generation."""
    print_header("🏗️ CloudFormation Generator Demo")
    
    cfn = CloudFormationGenerator()
    
    description = "A VPC with an EC2 web server and an RDS database"
    print(f"Infrastructure Description:\n  {description}\n")
    
    template = cfn.generate_from_description(description)
    print("Generated CloudFormation Template:")
    print("-" * 60)
    print(template[:800] + "\n... (truncated)")
    print("-" * 60)


def demo_excalidraw():
    """Demo Excalidraw diagram generation."""
    print_header("🎨 Architecture Diagram Demo")
    
    excalidraw = ExcalidrawService()
    
    description = "Web application with ALB, EC2 instances, and RDS database"
    print(f"Architecture Description:\n  {description}\n")
    
    diagram = excalidraw.generate_diagram(description)
    print(f"Generated Excalidraw Diagram:")
    print(f"  Elements: {len(diagram['elements'])}")
    print(f"  Type: {diagram['type']}")
    
    url = excalidraw.get_embed_url(diagram)
    print(f"  Excalidraw URL: {url[:80]}...")


def demo_ec2_instances():
    """Demo EC2 instance data."""
    print_header("☁️ EC2 Instances Demo")
    
    aws_service = MockAWSService()
    instances = aws_service.get_ec2_instances()
    
    print(f"Found {len(instances)} EC2 instances:\n")
    
    for instance in instances:
        print(f"  {instance['name']} ({instance['id']})")
        print(f"    Type: {instance['type']}")
        print(f"    State: {instance['state']}")
        print(f"    Utilization: {instance['utilization']}%")
        print(f"    Monthly Cost: ${instance['monthly_cost']:.2f}\n")


def demo_s3_buckets():
    """Demo S3 bucket data."""
    print_header("🪣 S3 Buckets Demo")
    
    aws_service = MockAWSService()
    buckets = aws_service.get_s3_buckets()
    
    print(f"Found {len(buckets)} S3 buckets:\n")
    
    for bucket in buckets:
        print(f"  {bucket['name']}")
        print(f"    Size: {bucket['size_gb']:.2f} GB")
        print(f"    Storage Class: {bucket['storage_class']}")
        print(f"    Objects: {bucket['objects']:,}")
        print(f"    Monthly Cost: ${bucket['monthly_cost']:.2f}\n")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  ☁️  NIMBUS COPILOT - DEMO")
    print("=" * 60)
    print("\n  Your personal AI DevOps team for AWS")
    print("  Deploy faster • Understand bills • Cut costs\n")
    
    demos = [
        ("Agent Orchestrator", demo_orchestrator),
        ("Cost Analysis", demo_cost_analysis),
        ("CloudFormation Generation", demo_cloudformation),
        ("Architecture Diagrams", demo_excalidraw),
        ("EC2 Instances", demo_ec2_instances),
        ("S3 Buckets", demo_s3_buckets),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo '{name}' failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("  Start the full app with: streamlit run app.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
