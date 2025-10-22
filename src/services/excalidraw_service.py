"""
Excalidraw integration for architecture diagram generation.
"""
import json
from typing import Dict, Any, List


class ExcalidrawService:
    """Service for generating Excalidraw architecture diagrams."""
    
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
