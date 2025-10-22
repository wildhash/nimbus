#!/usr/bin/env python3
"""
Simple test script to verify Nimbus Copilot core functionality.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.models.router import ModelRouter, ModelResponse
        print("✓ Model router imports OK")
    except Exception as e:
        print(f"✗ Model router import failed: {e}")
        return False
    
    try:
        from src.agents.base import BaseAgent
        from src.agents.setup_buddy import SetupBuddyAgent
        from src.agents.doc_navigator import DocNavigatorAgent
        from src.agents.bill_explainer import BillExplainerAgent
        from src.agents.cost_optimizer import CostOptimizerAgent
        print("✓ All agents import OK")
    except Exception as e:
        print(f"✗ Agent imports failed: {e}")
        return False
    
    try:
        from src.services.rag_service import RAGService, get_seed_documents
        from src.services.aws_service import MockAWSService, get_aws_service
        from src.services.excalidraw_service import ExcalidrawService
        print("✓ All services import OK")
    except Exception as e:
        print(f"✗ Service imports failed: {e}")
        return False
    
    try:
        from src.utils.cloudformation import CloudFormationGenerator
        print("✓ Utilities import OK")
    except Exception as e:
        print(f"✗ Utility imports failed: {e}")
        return False
    
    try:
        from src.orchestrator import AgentOrchestrator
        print("✓ Orchestrator imports OK")
    except Exception as e:
        print(f"✗ Orchestrator import failed: {e}")
        return False
    
    return True


def test_model_router():
    """Test model router with mock responses."""
    print("\nTesting model router...")
    
    from src.models.router import ModelRouter
    
    router = ModelRouter()
    response = router.generate("Hello, test query")
    
    if response.text and response.provider == "mock":
        print("✓ Model router returns mock responses when no API keys")
        return True
    else:
        print("✗ Model router test failed")
        return False


def test_agents():
    """Test agent initialization."""
    print("\nTesting agents...")
    
    from src.models.router import ModelRouter
    from src.agents.setup_buddy import SetupBuddyAgent
    from src.agents.doc_navigator import DocNavigatorAgent
    from src.agents.bill_explainer import BillExplainerAgent
    from src.agents.cost_optimizer import CostOptimizerAgent
    
    router = ModelRouter()
    
    try:
        setup = SetupBuddyAgent(router)
        docs = DocNavigatorAgent(router)
        bills = BillExplainerAgent(router)
        optimizer = CostOptimizerAgent(router)
        print("✓ All agents initialize successfully")
        return True
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        return False


def test_orchestrator():
    """Test orchestrator routing."""
    print("\nTesting orchestrator...")
    
    from src.models.router import ModelRouter
    from src.orchestrator import AgentOrchestrator
    
    router = ModelRouter()
    orchestrator = AgentOrchestrator(router)
    
    # Test routing
    test_cases = [
        ("How do I create a VPC?", "setup"),
        ("What is EC2?", "docs"),
        ("Why is my bill high?", "bills"),
        ("How can I reduce costs?", "optimize"),
    ]
    
    all_passed = True
    for query, expected_agent in test_cases:
        agent = orchestrator.route_query(query)
        if agent == expected_agent:
            print(f"  ✓ '{query}' → {agent}")
        else:
            print(f"  ✗ '{query}' → {agent} (expected {expected_agent})")
            all_passed = False
    
    return all_passed


def test_services():
    """Test services."""
    print("\nTesting services...")
    
    # Test AWS service
    from src.services.aws_service import MockAWSService
    
    aws = MockAWSService()
    cost_data = aws.get_cost_data()
    
    if cost_data and 'cost_history' in cost_data:
        print("✓ AWS service returns mock data")
    else:
        print("✗ AWS service test failed")
        return False
    
    # Test Excalidraw service
    from src.services.excalidraw_service import ExcalidrawService
    
    excalidraw = ExcalidrawService()
    diagram = excalidraw.generate_diagram("VPC with EC2 and RDS")
    
    if diagram and 'elements' in diagram:
        print("✓ Excalidraw service generates diagrams")
    else:
        print("✗ Excalidraw service test failed")
        return False
    
    # Test CloudFormation generator
    from src.utils.cloudformation import CloudFormationGenerator
    
    cfn = CloudFormationGenerator()
    template = cfn.generate_from_description("VPC with EC2 instance")
    
    if template and 'AWSTemplateFormatVersion' in template:
        print("✓ CloudFormation generator works")
    else:
        print("✗ CloudFormation generator test failed")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Nimbus Copilot - Core Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Model Router", test_model_router),
        ("Agents", test_agents),
        ("Orchestrator", test_orchestrator),
        ("Services", test_services),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
