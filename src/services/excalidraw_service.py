"""
Excalidraw integration for architecture diagram generation.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExcalidrawService:
    """Service for generating Excalidraw architecture diagrams."""
    
    def __init__(self):
        """Initialize the Excalidraw service."""
        self.storage_path = Path("./mock_data/diagrams")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def generate_diagram(self, infrastructure_desc: str) -> Dict[str, Any]:
        """
        Generate an Excalidraw diagram from infrastructure description.
        Returns Excalidraw JSON format.
        """
        # Parse infrastructure components
        components = self._parse_components(infrastructure_desc)
        
        # Generate Excalidraw elements
        elements = []
        x_offset = 100
        y_offset = 100
        spacing = 200
        
        # Add components as rectangles
        for i, comp in enumerate(components):
            element = self._create_rectangle(
                id=f"comp-{i}",
                x=x_offset + (i % 3) * spacing,
                y=y_offset + (i // 3) * spacing,
                width=150,
                height=80,
                text=comp["name"]
            )
            elements.append(element)
        
        # Add connections (arrows) between components
        for i in range(len(components) - 1):
            arrow = self._create_arrow(
                id=f"arrow-{i}",
                start_id=f"comp-{i}",
                end_id=f"comp-{i+1}"
            )
            elements.append(arrow)
        
        # Create Excalidraw JSON structure
        diagram = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://nimbus-copilot.local",
            "elements": elements,
            "appState": {
                "viewBackgroundColor": "#ffffff",
                "currentItemFontFamily": 1,
                "gridSize": 20
            }
        }
        
        return diagram
    
    def _parse_components(self, description: str) -> List[Dict[str, str]]:
        """Parse infrastructure components from description."""
        # Simple parsing - in production, this would use NLP or LLM
        components = []
        
        # Common AWS services to look for
        service_keywords = {
            "EC2": ["ec2", "instance", "server", "compute"],
            "S3": ["s3", "bucket", "storage"],
            "RDS": ["rds", "database", "db"],
            "Lambda": ["lambda", "function"],
            "VPC": ["vpc", "network"],
            "ALB": ["alb", "load balancer", "elb"],
            "CloudFront": ["cloudfront", "cdn"],
            "Route53": ["route53", "dns"]
        }
        
        desc_lower = description.lower()
        
        for service, keywords in service_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                components.append({
                    "name": service,
                    "type": "aws-service"
                })
        
        # Add some default components if none found
        if not components:
            components = [
                {"name": "VPC", "type": "aws-service"},
                {"name": "EC2", "type": "aws-service"},
                {"name": "RDS", "type": "aws-service"}
            ]
        
        return components
    
    def _create_rectangle(
        self,
        id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        text: str
    ) -> Dict[str, Any]:
        """Create an Excalidraw rectangle element."""
        return {
            "id": id,
            "type": "rectangle",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "#a5d8ff",
            "fillStyle": "hachure",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": {"type": 3},
            "seed": 12345,
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": 16,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "baseline": 14
        }
    
    def _create_arrow(
        self,
        id: str,
        start_id: str,
        end_id: str
    ) -> Dict[str, Any]:
        """Create an Excalidraw arrow element."""
        return {
            "id": id,
            "type": "arrow",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 0,
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "hachure",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "roundness": {"type": 2},
            "seed": 12346,
            "version": 1,
            "versionNonce": 1,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [100, 0]],
            "lastCommittedPoint": None,
            "startBinding": {"elementId": start_id, "focus": 0, "gap": 1},
            "endBinding": {"elementId": end_id, "focus": 0, "gap": 1},
            "startArrowhead": None,
            "endArrowhead": "arrow"
        }
    
    def export_to_json(self, diagram: Dict[str, Any]) -> str:
        """Export diagram to JSON string."""
        return json.dumps(diagram, indent=2)
    
    def get_embed_url(self, diagram: Dict[str, Any]) -> str:
        """Get Excalidraw embed URL for the diagram."""
        # Encode diagram as base64 for URL
        import base64
        diagram_json = json.dumps(diagram)
        encoded = base64.b64encode(diagram_json.encode()).decode()
        
        # Return URL to Excalidraw with encoded diagram
        return f"https://excalidraw.com/#json={encoded}"
    
    def save_board(
        self,
        board: Dict[str, Any],
        tenant: str = "default",
        session: str = "default"
    ) -> Dict[str, Any]:
        """
        Save Excalidraw board to storage (S3 or local).
        
        Args:
            board: Excalidraw board JSON
            tenant: Tenant identifier
            session: Session identifier
            
        Returns:
            Dictionary with save metadata
        """
        timestamp = datetime.now().isoformat()
        
        # Generate filename
        filename = f"{tenant}_{session}_{timestamp}.json"
        filepath = self.storage_path / filename
        
        # Save board JSON
        try:
            with open(filepath, 'w') as f:
                json.dump(board, f, indent=2)
            
            # Update manifest
            manifest = self._update_manifest(tenant, session, filename)
            
            logger.info(f"Saved board to {filepath}")
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "timestamp": timestamp,
                "manifest": manifest
            }
        except Exception as e:
            logger.error(f"Failed to save board: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _update_manifest(
        self,
        tenant: str,
        session: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Update manifest.json with latest board version.
        
        Args:
            tenant: Tenant identifier
            session: Session identifier
            filename: Filename of saved board
            
        Returns:
            Updated manifest
        """
        manifest_path = self.storage_path / "manifest.json"
        
        # Load existing manifest or create new
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {"boards": {}}
        
        # Create key for this board
        board_key = f"{tenant}_{session}"
        
        # Initialize board entry if needed
        if board_key not in manifest["boards"]:
            manifest["boards"][board_key] = {
                "tenant": tenant,
                "session": session,
                "history": []
            }
        
        # Add to history
        manifest["boards"][board_key]["history"].append({
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update latest key
        manifest["boards"][board_key]["latest_key"] = filename
        
        # Save manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    def board_to_cfn(self, board: Dict[str, Any]) -> str:
        """
        Convert Excalidraw board to CloudFormation template.
        Maps top 8 AWS shapes to CFN blocks.
        
        Args:
            board: Excalidraw board JSON
            
        Returns:
            CloudFormation template as YAML string
        """
        elements = board.get("elements", [])
        
        # Map of shape types to CFN resources
        shape_mapping = {
            "lambda": "AWS::Lambda::Function",
            "api": "AWS::ApiGateway::RestApi",
            "apigateway": "AWS::ApiGateway::RestApi",
            "dynamodb": "AWS::DynamoDB::Table",
            "s3": "AWS::S3::Bucket",
            "rds": "AWS::RDS::DBInstance",
            "alb": "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "vpc": "AWS::EC2::VPC",
            "subnet": "AWS::EC2::Subnet"
        }
        
        # Extract text labels and shapes
        texts = []
        shapes = []
        
        for element in elements:
            elem_type = element.get("type", "")
            if elem_type == "text":
                texts.append(element)
            elif elem_type in ["rectangle", "ellipse", "diamond"]:
                shapes.append(element)
        
        # Identify resources from shapes
        resources = {}
        resource_counter = {}
        
        for shape in shapes:
            # Find associated text label
            label = self._find_label_for_shape(shape, texts)
            if not label:
                continue
            
            label_lower = label.lower()
            
            # Match to AWS resource type
            matched_type = None
            for keyword, cfn_type in shape_mapping.items():
                if keyword in label_lower:
                    matched_type = cfn_type
                    break
            
            if matched_type:
                # Generate unique resource name
                base_name = matched_type.split("::")[-1]
                if base_name not in resource_counter:
                    resource_counter[base_name] = 0
                resource_counter[base_name] += 1
                
                resource_name = f"{base_name}{resource_counter[base_name]}"
                
                # Create basic resource definition
                resources[resource_name] = {
                    "Type": matched_type,
                    "Properties": self._generate_properties(matched_type)
                }
        
        # Build CFN template
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Auto-generated from Excalidraw diagram",
            "Resources": resources,
            "Outputs": {}
        }
        
        # Add outputs for key resources
        for name, resource in resources.items():
            template["Outputs"][f"{name}Output"] = {
                "Description": f"Reference to {name}",
                "Value": {"Ref": name}
            }
        
        # Convert to YAML
        import yaml
        return yaml.dump(template, default_flow_style=False, sort_keys=False)
    
    def _find_label_for_shape(
        self,
        shape: Dict[str, Any],
        texts: List[Dict[str, Any]]
    ) -> str:
        """Find text label associated with a shape."""
        shape_x = shape.get("x", 0)
        shape_y = shape.get("y", 0)
        
        # Look for text within 100 pixels
        for text in texts:
            text_x = text.get("x", 0)
            text_y = text.get("y", 0)
            
            if abs(text_x - shape_x) < 100 and abs(text_y - shape_y) < 100:
                return text.get("text", "")
        
        return ""
    
    def _generate_properties(self, resource_type: str) -> Dict[str, Any]:
        """Generate basic properties for a CFN resource type."""
        properties = {}
        
        if resource_type == "AWS::Lambda::Function":
            properties = {
                "Runtime": "python3.11",
                "Handler": "index.handler",
                "Code": {
                    "ZipFile": "# Lambda function code"
                },
                "Role": {"Fn::Sub": "arn:aws:iam::${AWS::AccountId}:role/LambdaExecutionRole"}
            }
        elif resource_type == "AWS::S3::Bucket":
            properties = {
                "BucketName": {"Fn::Sub": "${AWS::StackName}-bucket"}
            }
        elif resource_type == "AWS::DynamoDB::Table":
            properties = {
                "TableName": {"Fn::Sub": "${AWS::StackName}-table"},
                "BillingMode": "PAY_PER_REQUEST",
                "AttributeDefinitions": [
                    {"AttributeName": "id", "AttributeType": "S"}
                ],
                "KeySchema": [
                    {"AttributeName": "id", "KeyType": "HASH"}
                ]
            }
        elif resource_type == "AWS::ApiGateway::RestApi":
            properties = {
                "Name": {"Fn::Sub": "${AWS::StackName}-api"}
            }
        elif resource_type == "AWS::RDS::DBInstance":
            properties = {
                "Engine": "mysql",
                "DBInstanceClass": "db.t3.micro",
                "AllocatedStorage": "20"
            }
        elif resource_type == "AWS::ElasticLoadBalancingV2::LoadBalancer":
            properties = {
                "Type": "application",
                "Scheme": "internet-facing"
            }
        elif resource_type == "AWS::EC2::VPC":
            properties = {
                "CidrBlock": "10.0.0.0/16"
            }
        elif resource_type == "AWS::EC2::Subnet":
            properties = {
                "CidrBlock": "10.0.1.0/24"
            }
        
        return properties
    
    def validate_board(self, board: Dict[str, Any]) -> List[str]:
        """
        Validate Excalidraw board and return warnings.
        
        Args:
            board: Excalidraw board JSON
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Check if board has elements
        elements = board.get("elements", [])
        if not elements:
            warnings.append("Board has no elements")
        
        # Check for minimum number of resources
        shapes = [e for e in elements if e.get("type") in ["rectangle", "ellipse", "diamond"]]
        if len(shapes) < 2:
            warnings.append("Board should have at least 2 resources for a meaningful architecture")
        
        # Check for text labels
        texts = [e for e in elements if e.get("type") == "text"]
        if len(texts) < len(shapes):
            warnings.append("Some shapes may be missing labels")
        
        return warnings
