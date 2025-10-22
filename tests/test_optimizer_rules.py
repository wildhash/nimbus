#!/usr/bin/env python3
"""
Test cost optimizer rules and calculations.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.cost_optimizer import CostOptimizerAgent
from src.models.router import ModelRouter


def test_rule_based_optimization():
    """Test deterministic rule-based optimization."""
    print("Test: Rule-based Optimization")
    
    router = ModelRouter()
    optimizer = CostOptimizerAgent(router)
    
    result = optimizer.analyze_resources()
    
    assert result is not None
    assert 'findings' in result
    assert 'total' in result
    assert isinstance(result['findings'], list)
    assert isinstance(result['total'], (int, float))
    
    print(f"✓ Rule-based optimization working")
    print(f"  Findings: {len(result['findings'])}")
    print(f"  Total savings: ${result['total']:.2f}/month\n")


def test_finding_structure():
    """Test that findings have correct structure."""
    print("Test: Finding Structure")
    
    router = ModelRouter()
    optimizer = CostOptimizerAgent(router)
    
    result = optimizer.analyze_resources()
    findings = result['findings']
    
    if findings:
        first = findings[0]
        assert 'type' in first
        assert 'resource' in first
        assert 'action' in first
        assert 'est_savings' in first
        
        print(f"✓ Finding structure valid")
        print(f"  Sample finding:")
        print(f"    Type: {first['type']}")
        print(f"    Resource: {first['resource']}")
        print(f"    Savings: ${first['est_savings']:.2f}/month\n")
    else:
        print("✓ No findings (expected if no data)\n")


def test_savings_calculation():
    """Test savings calculations."""
    print("Test: Savings Calculation")
    
    router = ModelRouter()
    optimizer = CostOptimizerAgent(router)
    
    result = optimizer.analyze_resources()
    
    # Manual sum check
    manual_total = sum(f.get('est_savings', 0) for f in result['findings'])
    
    assert abs(result['total'] - manual_total) < 0.01  # Allow for rounding
    
    print(f"✓ Savings calculated correctly")
    print(f"  Calculated total: ${result['total']:.2f}/month")
    print(f"  Manual sum: ${manual_total:.2f}/month\n")


def test_findings_sorted():
    """Test that findings are sorted by savings."""
    print("Test: Findings Sorted by Impact")
    
    router = ModelRouter()
    optimizer = CostOptimizerAgent(router)
    
    result = optimizer.analyze_resources()
    findings = result['findings']
    
    if len(findings) > 1:
        # Check that findings are sorted descending by savings
        for i in range(len(findings) - 1):
            assert findings[i]['est_savings'] >= findings[i+1]['est_savings']
        
        print(f"✓ Findings sorted by impact")
        print(f"  Highest: ${findings[0]['est_savings']:.2f}/month")
        print(f"  Lowest: ${findings[-1]['est_savings']:.2f}/month\n")
    else:
        print("✓ Sorting N/A (insufficient findings)\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Cost Optimizer Rules Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_rule_based_optimization,
        test_finding_structure,
        test_savings_calculation,
        test_findings_sorted
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
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
