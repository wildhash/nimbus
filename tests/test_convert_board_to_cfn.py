#!/usr/bin/env python3
"""
Test Excalidraw board to CloudFormation conversion.
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.excalidraw_service import ExcalidrawService


def get_sample_diagram():
    """Get a sample Excalidraw diagram."""
    return {
        "type": "excalidraw",
        "version": 2,
        "elements": [
            {
                "id": "vpc1",
                "type": "rectangle",
                "x": 100,
                "y": 100,
                "width": 600,
                "height": 400
            },
            {
                "id": "vpc1_label",
                "type": "text",
                "x": 110,
                "y": 110,
                "text": "VPC"
            },
            {
                "id": "ec2_1",
                "type": "rectangle",
                "x": 150,
                "y": 200,
                "width": 100,
                "height": 80
            },
            {
                "id": "ec2_1_label",
                "type": "text",
                "x": 160,
                "y": 210,
                "text": "Web Server"
            },
            {
                "id": "rds_1",
                "type": "rectangle",
                "x": 400,
                "y": 200,
                "width": 100,
                "height": 80
            },
            {
                "id": "rds_1_label",
                "type": "text",
                "x": 410,
                "y": 210,
                "text": "RDS Database"
            },
            {
                "id": "s3_1",
                "type": "ellipse",
                "x": 300,
                "y": 350,
                "width": 100,
                "height": 80
            },
            {
                "id": "s3_1_label",
                "type": "text",
                "x": 310,
                "y": 360,
                "text": "S3 Bucket"
            },
            {
                "id": "arrow1",
                "type": "arrow",
                "startBinding": {"elementId": "ec2_1"},
                "endBinding": {"elementId": "rds_1"}
            },
            {
                "id": "arrow2",
                "type": "arrow",
                "startBinding": {"elementId": "ec2_1"},
                "endBinding": {"elementId": "s3_1"}
            }
        ]
    }


def test_resource_identification():
    """Test that resources are correctly identified."""
    print("Test: Resource Identification")
    
    diagram = get_sample_diagram()
    service = ExcalidrawService()
    cfn_yaml = service.board_to_cfn(diagram)
    
    assert cfn_yaml is not None
    assert len(cfn_yaml) > 0
    assert "AWSTemplateFormatVersion" in cfn_yaml
    assert "Resources:" in cfn_yaml
    
    print(f"✓ CFN template generated")
    print(f"  Template size: {len(cfn_yaml)} chars\n")


def test_resource_types():
    """Test that resource types are correctly mapped."""
    print("Test: Resource Type Mapping")
    
    diagram = get_sample_diagram()
    service = ExcalidrawService()
    cfn_yaml = service.board_to_cfn(diagram)
    
    # Check for AWS resource types in YAML
    assert "AWS::" in cfn_yaml
    
    print(f"✓ Resource types found in template")
    print(f"  Sample:\n{cfn_yaml[:300]}...\n")


def test_cfn_template_structure():
    """Test that CloudFormation template has correct structure."""
    print("Test: CloudFormation Template Structure")
    
    diagram = get_sample_diagram()
    service = ExcalidrawService()
    cfn_yaml = service.board_to_cfn(diagram)
    
    # Check required sections
    assert "AWSTemplateFormatVersion" in cfn_yaml
    assert "Resources:" in cfn_yaml
    assert "Outputs:" in cfn_yaml
    
    print("✓ Template structure valid")
    print(f"  Has version, resources, and outputs\n")


def test_yaml_output():
    """Test that template can be converted to YAML."""
    print("Test: YAML Output")
    
    diagram = get_sample_diagram()
    service = ExcalidrawService()
    yaml_output = service.board_to_cfn(diagram)
    
    assert yaml_output is not None
    assert len(yaml_output) > 0
    assert 'AWSTemplateFormatVersion' in yaml_output
    assert 'Resources:' in yaml_output
    
    print("✓ YAML output generated:")
    print()
    print(yaml_output[:500])
    print("...")
    print()


def test_empty_diagram():
    """Test handling of empty diagram."""
    print("Test: Empty Diagram Handling")
    
    empty_diagram = {
        "type": "excalidraw",
        "version": 2,
        "elements": []
    }
    
    service = ExcalidrawService()
    cfn_yaml = service.board_to_cfn(empty_diagram)
    
    assert cfn_yaml is not None
    assert "AWSTemplateFormatVersion" in cfn_yaml
    
    print("✓ Empty diagram handled gracefully")
    print(f"  Generated valid template\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Excalidraw to CloudFormation Conversion Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_resource_identification,
        test_resource_types,
        test_cfn_template_structure,
        test_yaml_output,
        test_empty_diagram
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}\n")
            import traceback
            traceback.print_exc()
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
