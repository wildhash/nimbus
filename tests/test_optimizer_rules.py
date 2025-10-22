#!/usr/bin/env python3
"""
Test cost optimizer rules and calculations.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.utils.aws_clients import AWSClients


def test_idle_ec2_detection():
    """Test idle EC2 instance detection."""
    print("Test: Idle EC2 Instance Detection")
    
    aws = AWSClients()
    instances = aws.list_idle_ec2_instances()
    
    assert instances is not None
    assert isinstance(instances, list)
    
    if instances:
        # Verify structure
        first = instances[0]
        assert 'instance_id' in first
        assert 'instance_type' in first
        
        # Calculate total potential savings
        total_savings = sum(inst.get('monthly_cost', 0) for inst in instances)
        
        print(f"✓ Found {len(instances)} potentially idle instances")
        print(f"  Total potential savings: ${total_savings:.2f}/month")
        
        for inst in instances[:3]:  # Show first 3
            print(f"  - {inst['instance_id']}: ${inst.get('monthly_cost', 0):.2f}/mo")
    else:
        print("✓ No idle instances found")
    
    print()


def test_old_snapshot_detection():
    """Test old snapshot detection."""
    print("Test: Old Snapshot Detection")
    
    aws = AWSClients()
    snapshots = aws.list_old_snapshots(days_old=90)
    
    assert snapshots is not None
    assert isinstance(snapshots, list)
    
    if snapshots:
        first = snapshots[0]
        assert 'snapshot_id' in first
        assert 'volume_size' in first
        
        total_size = sum(snap.get('volume_size', 0) for snap in snapshots)
        total_cost = sum(snap.get('monthly_cost', 0) for snap in snapshots)
        
        print(f"✓ Found {len(snapshots)} old snapshots")
        print(f"  Total size: {total_size} GB")
        print(f"  Monthly cost: ${total_cost:.2f}")
    else:
        print("✓ No old snapshots found")
    
    print()


def test_s3_lifecycle_opportunities():
    """Test S3 lifecycle optimization detection."""
    print("Test: S3 Lifecycle Opportunities")
    
    aws = AWSClients()
    opportunities = aws.analyze_s3_lifecycle_opportunities()
    
    assert opportunities is not None
    assert isinstance(opportunities, list)
    
    if opportunities:
        first = opportunities[0]
        assert 'bucket_name' in first
        assert 'recommendation' in first
        
        total_savings = sum(opp.get('estimated_savings', 0) for opp in opportunities)
        
        print(f"✓ Found {len(opportunities)} S3 optimization opportunities")
        print(f"  Total potential savings: ${total_savings:.2f}/month")
        
        for opp in opportunities[:3]:
            print(f"  - {opp['bucket_name']}: ${opp.get('estimated_savings', 0):.2f}/mo")
    else:
        print("✓ All S3 buckets optimized")
    
    print()


def test_cost_data_retrieval():
    """Test cost data retrieval."""
    print("Test: Cost Data Retrieval")
    
    aws = AWSClients()
    cost_data = aws.get_cost_data()
    
    assert cost_data is not None
    assert 'total_cost' in cost_data
    assert 'cost_by_service' in cost_data
    
    total = cost_data['total_cost']
    services = cost_data['cost_by_service']
    
    print(f"✓ Retrieved cost data")
    print(f"  Total cost: ${total:.2f}")
    print(f"  Services: {len(services)}")
    
    # Show top 3 services
    top_services = sorted(services.items(), key=lambda x: x[1], reverse=True)[:3]
    for service, cost in top_services:
        print(f"  - {service}: ${cost:.2f}")
    
    print()


def test_total_optimization_potential():
    """Calculate total optimization potential."""
    print("Test: Total Optimization Potential")
    
    aws = AWSClients()
    
    # Get all optimization opportunities
    idle_instances = aws.list_idle_ec2_instances()
    old_snapshots = aws.list_old_snapshots()
    s3_opportunities = aws.analyze_s3_lifecycle_opportunities()
    
    # Calculate totals
    ec2_savings = sum(inst.get('monthly_cost', 0) for inst in idle_instances)
    snapshot_savings = sum(snap.get('monthly_cost', 0) for snap in old_snapshots)
    s3_savings = sum(opp.get('estimated_savings', 0) for opp in s3_opportunities)
    
    total_savings = ec2_savings + snapshot_savings + s3_savings
    
    print(f"✓ Calculated total optimization potential")
    print(f"  EC2 idle instances: ${ec2_savings:.2f}/mo")
    print(f"  Old snapshots: ${snapshot_savings:.2f}/mo")
    print(f"  S3 lifecycle: ${s3_savings:.2f}/mo")
    print(f"  TOTAL: ${total_savings:.2f}/mo")
    print()
    
    assert total_savings >= 0


def main():
    """Run all tests."""
    print("=" * 60)
    print("Cost Optimizer Rules Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_idle_ec2_detection,
        test_old_snapshot_detection,
        test_s3_lifecycle_opportunities,
        test_cost_data_retrieval,
        test_total_optimization_potential
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
