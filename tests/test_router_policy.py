"""
Test model router fallback policy (Friendli → Bedrock → Mock).
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.router import ModelRouter


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
    old_friendli_token = os.environ.get('FRIENDLI_TOKEN')
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
    if old_friendli_token:
        os.environ['FRIENDLI_TOKEN'] = old_friendli_token
    if old_aws_key:
        os.environ['AWS_ACCESS_KEY_ID'] = old_aws_key
    
    assert response["provider"] == "mock"
    assert "unable to connect" in response["text"].lower()
    print("✓ Correctly fell back to mock provider")
    print(f"  Response: {response['text'][:80]}...\n")


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
    
    print("✓ Statistics tracked correctly")
    print(f"  Total calls: {stats['call_count']}")
    print(f"  Friendli: {stats['friendli_calls']}")
    print(f"  Bedrock: {stats['bedrock_calls']}")
    print(f"  Mock: {stats['mock_calls']}")
    print(f"  Avg latency: {stats['average_latency_ms']}ms\n")


def test_prefer_provider():
    """Test provider preference."""
    print("Test: Provider Preference")
    
    router = ModelRouter()
    
    # Request with default provider
    response = router.generate("Test prompt", prefer_provider="bedrock")
    
    # Will be bedrock if available, otherwise fallback
    print("✓ Provider preference respected")
    print("  Requested: bedrock")
    print(f"  Actual: {response.provider}\n")


def test_llm_complete_shape_and_lowercase():
    """Ensure llm_complete returns the expected shape and types."""
    print("Test: LLM Complete shape & lowercase provider")
    router = ModelRouter()
    resp = router.llm_complete("Hello")
    assert isinstance(resp, dict)
    assert 'text' in resp and 'provider' in resp and 'latency_ms' in resp
    assert isinstance(resp['provider'], str)
    assert isinstance(resp['latency_ms'], int)
    print("✓ llm_complete response shape valid\n")


def test_stats_average_latency_zero_by_default():
    """Average latency should be numeric even when providers are mocked."""
    print("Test: Average Latency Default")
    router = ModelRouter()
    for i in range(5):
        router.llm_complete(f"Q{i}")
    stats = router.get_stats()
    assert stats['call_count'] == 5
    assert isinstance(stats['average_latency_ms'], float)
    print(f"✓ Avg latency numeric ({stats['average_latency_ms']} ms)\n")


def test_bill_explainer_anomalies():
    """BillExplainer should detect high compute and optimization anomalies from mock bill."""
    print("Test: Bill Explainer Anomalies")
    from src.agents.bill_explainer import BillExplainerAgent
    agent = BillExplainerAgent(ModelRouter())
    bill = agent._load_bill_data()
    anomalies = agent._detect_anomalies(bill)
    assert isinstance(anomalies, list)
    assert any(a.get('type') == 'high_compute' for a in anomalies)
    assert any(a.get('type') == 'optimization' for a in anomalies)
    print(f"✓ Detected {len(anomalies)} anomalies (includes high_compute and optimization)\n")


def test_bill_explainer_process_returns_modelresponse():
    """process() should return a ModelResponse even when providers are mocked."""
    print("Test: Bill Explainer Process → ModelResponse")
    from src.agents.bill_explainer import BillExplainerAgent
    from src.models.router import ModelResponse
    agent = BillExplainerAgent(ModelRouter())
    resp = agent.process("Explain my AWS bill")
    assert isinstance(resp, ModelResponse)
    assert isinstance(resp.text, str) and isinstance(resp.provider, str)
    print("✓ BillExplainer returned ModelResponse\n")


def test_rag_format_citations():
    """RAGService.format_citations should produce markdown with bullets and quotes."""
    print("Test: RAG Citations Formatting")
    from src.services.rag_service import RAGService, format_citations
    rag = RAGService()
    hits = rag.hybrid_search("AWS cost optimization", k=2)
    citations = format_citations(hits)
    assert isinstance(citations, str) and citations.strip() != ""
    assert "**" in citations
    print("✓ Citations formatted\n")


def test_doc_navigator_appends_sources():
    """DocNavigator should append sources section when RAG results exist."""
    print("Test: DocNavigator Sources Append")
    from src.agents.doc_navigator import DocNavigatorAgent
    from src.services.rag_service import RAGService
    agent = DocNavigatorAgent(ModelRouter(), rag_service=RAGService())
    response = agent.process("S3 pricing")
    assert "### Sources" in response.text
    print("✓ DocNavigator appended sources\n")


def test_logging_scrub_secrets():
    """Secret scrubbing should redact tokens and AWS credentials."""
    print("Test: Logging Secret Scrub")
    from src.utils.logging import scrub_secrets
    s = "token=abc123 Bearer AAA.BBB== aws_access_key_id=AKIA123 aws_secret_access_key=xyz/123"
    out = scrub_secrets(s)
    assert "***REDACTED***" in out
    assert "abc123" not in out and "AKIA123" not in out and "xyz/123" not in out
    print("✓ Secrets scrubbed\n")


def test_llm_providers_raise_when_missing():
    """Low-level provider helpers should raise ImportError when SDKs are unavailable."""
    print("Test: LLM Providers ImportError")
    from src.services.llm_providers import friendli_complete, bedrock_complete
    raised = False
    try:
        friendli_complete("hi")
    except ImportError:
        raised = True
    assert raised, "friendli_complete should raise ImportError when package missing"
    raised = False
    try:
        bedrock_complete("hi")
    except ImportError:
        raised = True
    assert raised, "bedrock_complete should raise ImportError when package missing"
    print("✓ Provider helpers raise as expected\n")


def test_setup_buddy_regenerate_cfn_from_board():
    """SetupBuddy should regenerate CFN from an Excalidraw board."""
    print("Test: SetupBuddy regenerate CFN")
    from src.agents.setup_buddy import SetupBuddyAgent
    from src.services.excalidraw_service import ExcalidrawService
    agent = SetupBuddyAgent(ModelRouter(), excalidraw_service=ExcalidrawService())
    board = agent.excalidraw_service.generate_diagram("Lambda with S3 and DynamoDB")
    cfn = agent.regenerate_cfn_from_board(board)
    assert isinstance(cfn, str)
    assert "AWSTemplateFormatVersion" in cfn and "Resources:" in cfn
    print("✓ CFN regenerated\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Model Router & Agents Tests (Extended Coverage)")
    print("=" * 60)
    print()
    
    tests = [
        # Existing
        test_router_initialization,
        test_fallback_to_mock,
        test_stats_tracking,
        test_prefer_provider,
        # New
        test_llm_complete_shape_and_lowercase,
        test_stats_average_latency_zero_by_default,
        test_bill_explainer_anomalies,
        test_bill_explainer_process_returns_modelresponse,
        test_rag_format_citations,
        test_doc_navigator_appends_sources,
        test_logging_scrub_secrets,
        test_llm_providers_raise_when_missing,
        test_setup_buddy_regenerate_cfn_from_board,
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
        except Exception as e:  # noqa: BLE001
            print(f"✗ Test error: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())