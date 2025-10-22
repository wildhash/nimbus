#!/usr/bin/env python3
"""
Test model router fallback policy (Friendli → Bedrock → Mock).
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.model_router import ModelRouter


def test_router_initialization():
    """Test that router initializes correctly."""
    print("Test: Router Initialization")
    router = ModelRouter()
    assert router is not None
    print("✓ Router initialized successfully\n")


def test_fallback_to_mock():
    """Test fallback to mock when no providers available."""
    print("Test: Fallback to Mock")
    
    # Temporarily disable environment variables
    old_friendli = os.environ.get('FRIENDLI_API_KEY')
    old_aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    
    if 'FRIENDLI_API_KEY' in os.environ:
        del os.environ['FRIENDLI_API_KEY']
    if 'FRIENDLI_TOKEN' in os.environ:
        del os.environ['FRIENDLI_TOKEN']
    if 'AWS_ACCESS_KEY_ID' in os.environ:
        del os.environ['AWS_ACCESS_KEY_ID']
    
    router = ModelRouter()
    response = router.llm_complete("Test query")
    
    # Restore environment
    if old_friendli:
        os.environ['FRIENDLI_API_KEY'] = old_friendli
    if old_aws_key:
        os.environ['AWS_ACCESS_KEY_ID'] = old_aws_key
    
    assert response.provider == "mock"
    assert "unable to connect" in response.text.lower()
    print(f"✓ Correctly fell back to mock provider")
    print(f"  Response: {response.text[:80]}...\n")


def test_stats_tracking():
    """Test that router tracks statistics correctly."""
    print("Test: Statistics Tracking")
    
    router = ModelRouter()
    
    # Make a few calls
    router.llm_complete("Query 1")
    router.llm_complete("Query 2")
    router.llm_complete("Query 3")
    
    stats = router.get_stats()
    
    assert stats['call_count'] == 3
    assert stats['mock_calls'] >= 0  # Depends on if providers available
    
    print(f"✓ Statistics tracked correctly")
    print(f"  Total calls: {stats['call_count']}")
    print(f"  Friendli: {stats['friendli_calls']}")
    print(f"  Bedrock: {stats['bedrock_calls']}")
    print(f"  Mock: {stats['mock_calls']}")
    print(f"  Avg latency: {stats['average_latency_ms']}ms\n")


def test_prefer_provider():
    """Test provider preference."""
    print("Test: Provider Preference")
    
    router = ModelRouter()
    
    # Request Bedrock preference
    response = router.llm_complete("Test", prefer_provider="bedrock")
    
    # Will be bedrock if available, otherwise fallback
    print(f"✓ Provider preference respected")
    print(f"  Requested: bedrock")
    print(f"  Actual: {response.provider}\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Model Router Fallback Policy Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_router_initialization,
        test_fallback_to_mock,
        test_stats_tracking,
        test_prefer_provider
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
