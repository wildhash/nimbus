"""
Convert Excalidraw diagram shapes to CloudFormation hints.
"""
import json
from typing import Dict, Any, List, Optional


class ExcalidrawToCFNConverter:
    """Convert Excalidraw diagram elements to CloudFormation template hints."""
    
    # Map Excalidraw shapes to AWS resources
    SHAPE_TO_RESOURCE = {
        "rectangle": {
            "vpc": "AWS::EC2::VPC",
            "subnet": "AWS::EC2::Subnet",
            "instance": "AWS::EC2::Instance",
            "rds": "AWS::RDS::DBInstance",
            "lambda": "AWS::Lambda::Function"
        },
        "ellipse": {
            "s3": "AWS::S3::Bucket",
            "dynamodb": "AWS::DynamoDB::Table"
        },
        "diamond": {
            "gateway": "AWS::EC2::InternetGateway",
            "nat": "AWS::EC2::NatGateway",
            "alb": "AWS::ElasticLoadBalancingV2::LoadBalancer"
        }
    }
    
    def __init__(self):
        self.resources = {}
        self.connections = []
    
    def convert(self, excalidraw_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Excalidraw JSON to CloudFormation template hints.
        
        Args:
            excalidraw_json: Excalidraw diagram JSON
            
        Returns:
            Dictionary with CloudFormation template structure
        """
        elements = excalidraw_json.get('elements', [])
        
        # Parse elements
        shapes = []
        arrows = []
        texts = []
        
        for element in elements:
            elem_type = element.get('type')
            if elem_type in ['rectangle', 'ellipse', 'diamond']:
                shapes.append(element)
            elif elem_type == 'arrow':
                arrows.append(element)
            elif elem_type == 'text':
                texts.append(element)
        
        # Identify resources from shapes and labels
        resources = self._identify_resources(shapes, texts)
        
        # Identify connections from arrows
        connections = self._identify_connections(arrows, shapes)
        
        # Generate CloudFormation template
        cfn_template = self._generate_cfn_template(resources, connections)
        
        return cfn_template
    
    def _identify_resources(
        self,
        shapes: List[Dict[str, Any]],
        texts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify AWS resources from shapes and text labels."""
        resources = []
        
        # Create a map of text positions to text content
        text_map = {}
        for text in texts:
            x = text.get('x', 0)
            y = text.get('y', 0)
            content = text.get('text', '').lower()
            text_map[(x, y)] = content
        
        for shape in shapes:
            shape_type = shape.get('type')
            shape_id = shape.get('id')
            x = shape.get('x', 0)
            y = shape.get('y', 0)
            
            # Find nearby text (within 50 pixels)
            label = self._find_nearby_text(x, y, text_map)
            
            # Determine resource type
            resource_type = self._infer_resource_type(shape_type, label)
            
            if resource_type:
                resources.append({
                    'id': shape_id,
                    'type': resource_type,
                    'label': label or f'Resource{len(resources) + 1}',
                    'shape': shape_type,
                    'position': {'x': x, 'y': y}
                })
        
        return resources
    
    def _find_nearby_text(
        self,
        x: float,
        y: float,
        text_map: Dict[tuple, str],
        threshold: float = 100
    ) -> Optional[str]:
        """Find text near a given position."""
        for (tx, ty), content in text_map.items():
            distance = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
            if distance < threshold:
                return content
        return None
    
    def _infer_resource_type(self, shape_type: str, label: Optional[str]) -> Optional[str]:
        """Infer AWS resource type from shape and label."""
        if not label:
            # Default mapping based on shape
            if shape_type == 'rectangle':
                return 'AWS::EC2::Instance'
            elif shape_type == 'ellipse':
                return 'AWS::S3::Bucket'
            return None
        
        label_lower = label.lower()
        
        # Check for common AWS service keywords
        if 'vpc' in label_lower:
            return 'AWS::EC2::VPC'
        elif 'subnet' in label_lower:
            return 'AWS::EC2::Subnet'
        elif 'ec2' in label_lower or 'instance' in label_lower:
            return 'AWS::EC2::Instance'
        elif 'rds' in label_lower or 'database' in label_lower:
            return 'AWS::RDS::DBInstance'
        elif 's3' in label_lower or 'bucket' in label_lower:
            return 'AWS::S3::Bucket'
        elif 'lambda' in label_lower or 'function' in label_lower:
            return 'AWS::Lambda::Function'
        elif 'alb' in label_lower or 'load balancer' in label_lower:
            return 'AWS::ElasticLoadBalancingV2::LoadBalancer'
        elif 'gateway' in label_lower or 'igw' in label_lower:
            return 'AWS::EC2::InternetGateway'
        elif 'nat' in label_lower:
            return 'AWS::EC2::NatGateway'
        elif 'dynamo' in label_lower:
            return 'AWS::DynamoDB::Table'
        
        return 'AWS::EC2::Instance'  # Default
    
    def _identify_connections(
        self,
        arrows: List[Dict[str, Any]],
        shapes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify connections between resources."""
        connections = []
        
        for arrow in arrows:
            start_binding = arrow.get('startBinding')
            end_binding = arrow.get('endBinding')
            
            if start_binding and end_binding:
                connections.append({
                    'from': start_binding.get('elementId'),
                    'to': end_binding.get('elementId'),
                    'type': 'depends_on'
                })
        
        return connections
    
    def _generate_cfn_template(
        self,
        resources: List[Dict[str, Any]],
        connections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate CloudFormation template structure."""
        cfn_resources = {}
        
        for resource in resources:
            resource_id = resource['id']
            resource_type = resource['type']
            label = resource['label']
            
            # Generate logical resource name
            logical_name = self._to_logical_name(label)
            
            # Basic resource definition
            cfn_resources[logical_name] = {
                'Type': resource_type,
                'Properties': self._get_default_properties(resource_type),
                'Metadata': {
                    'DiagramId': resource_id,
                    'DiagramLabel': label
                }
            }
        
        # Add dependencies from connections
        for conn in connections:
            from_id = conn['from']
            to_id = conn['to']
            
            # Find logical names
            from_name = self._find_logical_name(from_id, resources, cfn_resources)
            to_name = self._find_logical_name(to_id, resources, cfn_resources)
            
            if from_name and to_name and from_name in cfn_resources:
                if 'DependsOn' not in cfn_resources[from_name]:
                    cfn_resources[from_name]['DependsOn'] = []
                cfn_resources[from_name]['DependsOn'].append(to_name)
        
        return {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'Generated from Excalidraw diagram',
            'Resources': cfn_resources,
            'Outputs': self._generate_outputs(cfn_resources)
        }
    
    def _to_logical_name(self, label: str) -> str:
        """Convert label to CloudFormation logical name."""
        # Remove special characters and capitalize words
        clean = ''.join(c if c.isalnum() else ' ' for c in label)
        words = clean.split()
        return ''.join(word.capitalize() for word in words) or 'Resource'
    
    def _get_default_properties(self, resource_type: str) -> Dict[str, Any]:
        """Get default properties for a resource type."""
        defaults = {
            'AWS::EC2::VPC': {
                'CidrBlock': '10.0.0.0/16',
                'EnableDnsHostnames': True,
                'EnableDnsSupport': True
            },
            'AWS::EC2::Subnet': {
                'CidrBlock': '10.0.1.0/24',
                'VpcId': {'Ref': 'VPC'}
            },
            'AWS::EC2::Instance': {
                'InstanceType': 't3.micro',
                'ImageId': 'ami-0c55b159cbfafe1f0'  # Placeholder
            },
            'AWS::S3::Bucket': {
                'BucketName': {'Fn::Sub': '${AWS::StackName}-bucket'}
            },
            'AWS::RDS::DBInstance': {
                'DBInstanceClass': 'db.t3.micro',
                'Engine': 'mysql',
                'AllocatedStorage': '20'
            },
            'AWS::Lambda::Function': {
                'Runtime': 'python3.9',
                'Handler': 'index.handler',
                'Code': {
                    'ZipFile': 'def handler(event, context):\n    return {"statusCode": 200}'
                }
            }
        }
        
        return defaults.get(resource_type, {})
    
    def _generate_outputs(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CloudFormation outputs."""
        outputs = {}
        
        for name, resource in resources.items():
            resource_type = resource['Type']
            
            if resource_type == 'AWS::EC2::Instance':
                outputs[f'{name}Id'] = {
                    'Description': f'Instance ID of {name}',
                    'Value': {'Ref': name}
                }
            elif resource_type == 'AWS::S3::Bucket':
                outputs[f'{name}Name'] = {
                    'Description': f'Name of {name}',
                    'Value': {'Ref': name}
                }
        
        return outputs
    
    def _find_logical_name(
        self,
        diagram_id: str,
        resources: List[Dict[str, Any]],
        cfn_resources: Dict[str, Any]
    ) -> Optional[str]:
        """Find CloudFormation logical name from diagram ID."""
        for resource in resources:
            if resource['id'] == diagram_id:
                label = resource['label']
                logical_name = self._to_logical_name(label)
                if logical_name in cfn_resources:
                    return logical_name
        return None


def convert_board_to_cfn(excalidraw_json: Dict[str, Any]) -> str:
    """
    Convert Excalidraw board to CloudFormation YAML.
    
    Args:
        excalidraw_json: Excalidraw diagram JSON
        
    Returns:
        CloudFormation template as YAML string
    """
    import yaml
    
    converter = ExcalidrawToCFNConverter()
    cfn_dict = converter.convert(excalidraw_json)
    
    return yaml.dump(cfn_dict, default_flow_style=False, sort_keys=False)
