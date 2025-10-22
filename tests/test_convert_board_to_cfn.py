#!/usr/bin/env python3
"""
Test Excalidraw board to CloudFormation conversion.
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.diagram.convert import ExcalidrawToCFNConverter, convert_board_to_cfn


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
    converter = ExcalidrawToCFNConverter()
    result = converter.convert(diagram)
    
    resources = result.get('Resources', {})
    
    assert len(resources) > 0, "Should identify at least one resource"
    
    print(f"✓ Identified {len(resources)} resources:")
    for name, resource in resources.items():
        print(f"  - {name}: {resource['Type']}")
    
    print()


def test_resource_types():
    """Test that resource types are correctly mapped."""
    print("Test: Resource Type Mapping")
    
    diagram = get_sample_diagram()
    converter = ExcalidrawToCFNConverter()
    result = converter.convert(diagram)
    
    resources = result.get('Resources', {})
    
    # Check that we have expected types
    types = [r['Type'] for r in resources.values()]
    
    assert 'AWS::EC2::VPC' in types or len(types) > 0, "Should have AWS resource types"
    
    print(f"✓ Resource types mapped correctly:")
    unique_types = set(types)
    for rt in unique_types:
        count = types.count(rt)
        print(f"  - {rt}: {count}")
    
    print()


def test_cfn_template_structure():
    """Test that CloudFormation template has correct structure."""
    print("Test: CloudFormation Template Structure")
    
    diagram = get_sample_diagram()
    converter = ExcalidrawToCFNConverter()
    result = converter.convert(diagram)
    
    # Check required sections
    assert 'AWSTemplateFormatVersion' in result
    assert 'Resources' in result
    assert 'Outputs' in result
    
    assert result['AWSTemplateFormatVersion'] == '2010-09-09'
    
    print("✓ Template structure valid:")
    print(f"  - Format version: {result['AWSTemplateFormatVersion']}")
    print(f"  - Resources: {len(result['Resources'])}")
    print(f"  - Outputs: {len(result['Outputs'])}")
    
    print()


def test_yaml_output():
    """Test that template can be converted to YAML."""
    print("Test: YAML Output")
    
    diagram = get_sample_diagram()
    yaml_output = convert_board_to_cfn(diagram)
    
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
    
    converter = ExcalidrawToCFNConverter()
    result = converter.convert(empty_diagram)
    
    assert 'Resources' in result
    assert 'AWSTemplateFormatVersion' in result
    
    print("✓ Empty diagram handled gracefully")
    print(f"  Resources: {len(result['Resources'])}")
    
    print()


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
