"""
Base agent class for Nimbus Copilot agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.models.router import ModelRouter, ModelResponse


class BaseAgent(ABC):
    """Base class for all Nimbus agents."""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.name = self.__class__.__name__
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process user input and return response."""
        pass
    
    def format_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Format context dictionary into a string for the prompt."""
        if not context:
            return ""
        
        formatted = "\n\nContext:\n"
        for key, value in context.items():
            formatted += f"- {key}: {value}\n"
        return formatted
