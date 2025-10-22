"""
Setup Buddy Agent - Helps users set up AWS infrastructure.
"""
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class SetupBuddyAgent(BaseAgent):
    """Agent specialized in AWS infrastructure setup and deployment."""
    
    def __init__(self, model_router, excalidraw_service=None):
        super().__init__(model_router)
        self.excalidraw_service = excalidraw_service
    
    def get_system_prompt(self) -> str:
        return """You are Setup Buddy, an expert AWS infrastructure consultant. Your role is to:

1. Help users design and deploy AWS infrastructure
2. Generate CloudFormation templates for common patterns
3. Provide best practices for security, scalability, and cost optimization
4. Guide users through the setup process step by step
5. Explain AWS services in simple terms
6. Create visual architecture diagrams

Always be friendly, clear, and practical. Focus on helping users get their infrastructure up and running quickly and correctly."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process setup-related queries."""
        
        # Add context to the prompt
        prompt = user_input
        if context:
            prompt += self.format_context(context)
        
        # Generate response using model router
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.7
        )
        
        return response
    
    def generate_cloudformation(self, infrastructure_desc: str) -> str:
        """Generate CloudFormation template based on description."""
        prompt = f"""Generate a CloudFormation template in YAML format for the following infrastructure:

{infrastructure_desc}

Include proper resource naming, dependencies, and outputs. Follow AWS best practices."""
        
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.text
    
    def generate_diagram(self, infrastructure_desc: str) -> Dict[str, Any]:
        """
        Generate an Excalidraw diagram from infrastructure description.
        
        Args:
            infrastructure_desc: Description of infrastructure
            
        Returns:
            Excalidraw diagram JSON and metadata
        """
        if not self.excalidraw_service:
            return {
                "success": False,
                "error": "Excalidraw service not available"
            }
        
        # Generate diagram
        diagram = self.excalidraw_service.generate_diagram(infrastructure_desc)
        
        # Save diagram
        save_result = self.excalidraw_service.save_board(diagram)
        
        # Get embed URL
        embed_url = self.excalidraw_service.get_embed_url(diagram)
        
        return {
            "success": True,
            "diagram": diagram,
            "embed_url": embed_url,
            "save_result": save_result
        }
    
    def regenerate_cfn_from_board(self, board: Dict[str, Any]) -> str:
        """
        Regenerate CloudFormation template from an Excalidraw board.
        
        Args:
            board: Excalidraw board JSON
            
        Returns:
            CloudFormation template as YAML string
        """
        if not self.excalidraw_service:
            return "# Error: Excalidraw service not available"
        
        # Validate board
        warnings = self.excalidraw_service.validate_board(board)
        
        # Convert board to CFN
        cfn_template = self.excalidraw_service.board_to_cfn(board)
        
        # Add warnings as comments if any
        if warnings:
            warning_text = "# Warnings:\n"
            for warning in warnings:
                warning_text += f"#   - {warning}\n"
            cfn_template = warning_text + "\n" + cfn_template
        
        return cfn_template
