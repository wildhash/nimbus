"""
Doc Navigator Agent - Helps users find and understand AWS documentation.
"""
from typing import Dict, Any, Optional, List
from src.agents.base import BaseAgent
from src.models.router import ModelResponse


class DocNavigatorAgent(BaseAgent):
    """Agent specialized in navigating AWS documentation using RAG."""
    
    def __init__(self, model_router, rag_service=None):
        super().__init__(model_router)
        self.rag_service = rag_service
    
    def get_system_prompt(self) -> str:
        return """You are Doc Navigator, an expert at helping users find and understand AWS documentation. Your role is to:

1. Search AWS documentation for relevant information
2. Explain complex AWS concepts in simple terms
3. Provide code examples and best practices from documentation
4. Point users to the right resources and guides
5. Summarize long documentation into key points

Be concise, accurate, and helpful. Always cite the source when referencing documentation."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Process documentation queries with RAG."""
        
        # Retrieve relevant documents if RAG service is available
        relevant_docs = ""
        if self.rag_service:
            docs = self.rag_service.search(user_input, limit=3)
            if docs:
                relevant_docs = "\n\nRelevant Documentation:\n"
                for i, doc in enumerate(docs, 1):
                    relevant_docs += f"\n{i}. {doc.get('title', 'AWS Documentation')}\n"
                    relevant_docs += f"   {doc.get('content', '')[:500]}...\n"
        
        # Build prompt with context and retrieved docs
        prompt = user_input + relevant_docs
        if context:
            prompt += self.format_context(context)
        
        # Generate response
        response = self.model_router.generate(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.5
        )
        
        return response
    
    def search_docs(self, query: str) -> List[Dict[str, Any]]:
        """Search for relevant documentation."""
        if self.rag_service:
            return self.rag_service.search(query, limit=5)
        return []
