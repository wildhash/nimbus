#!/usr/bin/env python3
"""
Comprehensive integration test for Nimbus Copilot backend.
Tests all major components working together.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_integration():
    """Run comprehensive integration test."""
    print("=" * 60)
    print("Nimbus Copilot - Complete Integration Test")
    print("=" * 60)
    print()
    
    # Test 1: Backend utilities
    print("1. Testing backend utilities...")
    from backend.utils.model_router import ModelRouter
    from backend.utils.weaviate_client import WeaviateClient
    from backend.utils.aws_clients import AWSClients
    
    router = ModelRouter()
    weaviate = WeaviateClient()
    aws = AWSClients()
    
    assert router is not None
    assert weaviate is not None
    assert aws is not None
    
    print("   ✓ Model router initialized")
    print("   ✓ Weaviate client initialized")
    print("   ✓ AWS clients initialized")
    print()
    
    # Test 2: All agents
    print("2. Testing all agents...")
    from backend.agents.setup_buddy import SetupBuddyAgent
    from backend.agents.bill_explainer import BillExplainerAgent
    from backend.agents.cost_optimizer import CostOptimizerAgent
    from backend.agents.doc_navigator import DocNavigatorAgent
    
    setup = SetupBuddyAgent(router, weaviate)
    bills = BillExplainerAgent(router, aws, weaviate)
    optimizer = CostOptimizerAgent(router, aws)
    docs = DocNavigatorAgent(router, weaviate)
    
    assert setup is not None
    assert bills is not None
    assert optimizer is not None
    assert docs is not None
    
    print("   ✓ Setup Buddy agent created")
    print("   ✓ Bill Explainer agent created")
    print("   ✓ Cost Optimizer agent created")
    print("   ✓ Doc Navigator agent created")
    print()
    
    # Test 3: LlamaIndex router
    print("3. Testing LlamaIndex agent router...")
    from backend.agents.llama.router import LlamaAgentRouter
    
    llama_router = LlamaAgentRouter(router, weaviate, aws)
    assert llama_router is not None
    
    # Test routing
    agent_name = llama_router.route_query("Deploy a web application")
    assert agent_name == "setup"
    
    agent_name = llama_router.route_query("Why is my bill high?")
    assert agent_name == "bills"
    
    agent_name = llama_router.route_query("How can I save money?")
    assert agent_name == "optimize"
    
    agent_name = llama_router.route_query("What is S3?")
    assert agent_name == "docs"
    
    print("   ✓ LlamaIndex router initialized")
    print("   ✓ Query routing working correctly")
    print()
    
    # Test 4: Agent responses
    print("4. Testing agent query processing...")
    
    # Doc Navigator
    response = docs.process("What is EC2?")
    assert response is not None
    assert hasattr(response, 'text')
    assert hasattr(response, 'provider')
    assert hasattr(response, 'latency_ms')
    print(f"   ✓ Doc Navigator: {response.text[:60]}...")
    print(f"     Provider: {response.provider}, Latency: {response.latency_ms}ms")
    
    # Setup Buddy
    response = setup.process("Create a simple web app")
    assert response is not None
    print(f"   ✓ Setup Buddy: {response.text[:60]}...")
    
    # Bill Explainer
    response = bills.explain_bill()
    assert response is not None
    print(f"   ✓ Bill Explainer: {response.text[:60]}...")
    print()
    
    # Test 5: Cost optimizer
    print("5. Testing cost optimizer...")
    
    savings = optimizer.get_savings_summary()
    assert 'total_monthly_savings' in savings
    assert 'ec2_idle_instances' in savings
    assert 'old_snapshots' in savings
    assert 's3_lifecycle' in savings
    
    print(f"   ✓ EC2 idle instances: {savings['ec2_idle_instances']['count']}")
    print(f"   ✓ Old snapshots: {savings['old_snapshots']['count']}")
    print(f"   ✓ S3 opportunities: {savings['s3_lifecycle']['count']}")
    print(f"   ✓ Total monthly savings: ${savings['total_monthly_savings']:.2f}")
    print()
    
    # Test 6: Weaviate search
    print("6. Testing Weaviate hybrid search...")
    
    docs_results = weaviate.hybrid_search('AWSDocs', 'EC2 pricing', limit=3)
    assert docs_results is not None
    assert len(docs_results) > 0
    
    print(f"   ✓ Found {len(docs_results)} documents")
    print(f"   ✓ First: {docs_results[0].get('title', 'N/A')}")
    print(f"   ✓ Service: {docs_results[0].get('service', 'N/A')}")
    print()
    
    # Test 7: AWS clients
    print("7. Testing AWS service clients...")
    
    cost_data = aws.get_cost_data()
    assert 'total_cost' in cost_data
    assert 'cost_by_service' in cost_data
    print(f"   ✓ Cost data: ${cost_data['total_cost']:.2f}")
    
    instances = aws.list_idle_ec2_instances()
    assert instances is not None
    print(f"   ✓ Idle instances: {len(instances)}")
    
    snapshots = aws.list_old_snapshots()
    assert snapshots is not None
    print(f"   ✓ Old snapshots: {len(snapshots)}")
    
    s3_opps = aws.analyze_s3_lifecycle_opportunities()
    assert s3_opps is not None
    print(f"   ✓ S3 opportunities: {len(s3_opps)}")
    print()
    
    # Test 8: Model router stats
    print("8. Testing model router statistics...")
    
    stats = router.get_stats()
    assert 'call_count' in stats
    assert 'friendli_calls' in stats
    assert 'bedrock_calls' in stats
    assert 'mock_calls' in stats
    
    print(f"   ✓ Total calls: {stats['call_count']}")
    print(f"   ✓ Friendli: {stats['friendli_calls']}")
    print(f"   ✓ Bedrock: {stats['bedrock_calls']}")
    print(f"   ✓ Mock: {stats['mock_calls']}")
    print(f"   ✓ Avg latency: {stats.get('average_latency_ms', 0):.2f}ms")
    print()
    
    # Test 9: Diagram conversion
    print("9. Testing Excalidraw to CloudFormation conversion...")
    from backend.diagram.convert import ExcalidrawToCFNConverter
    
    sample_diagram = {
        "type": "excalidraw",
        "elements": [
            {"id": "1", "type": "rectangle", "x": 100, "y": 100},
            {"id": "2", "type": "text", "x": 110, "y": 110, "text": "VPC"}
        ]
    }
    
    converter = ExcalidrawToCFNConverter()
    cfn = converter.convert(sample_diagram)
    
    assert 'AWSTemplateFormatVersion' in cfn
    assert 'Resources' in cfn
    print("   ✓ Diagram converter working")
    print(f"   ✓ Generated {len(cfn.get('Resources', {}))} resources")
    print()
    
    print("=" * 60)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print()
    print("System ready for deployment!")
    print("Run: streamlit run frontend/app.py")
    print()
    
    return True


def main():
    """Run all integration tests."""
    try:
        success = test_integration()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Integration test failed with error:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
