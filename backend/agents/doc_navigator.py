"""
Doc Navigator Agent - Enhanced with Weaviate semantic search.
"""
from typing import Dict, Any, Optional, List
from backend.utils.model_router import ModelRouter, LLMResponse
from backend.utils.weaviate_client import WeaviateClient


class DocNavigatorAgent:
    """Agent specialized in navigating AWS documentation using RAG."""
    
    def __init__(
        self,
        model_router: ModelRouter,
        weaviate_client: Optional[WeaviateClient] = None
    ):
        self.model_router = model_router
        self.weaviate_client = weaviate_client or WeaviateClient()
        self.name = "Doc Navigator"
    
    def get_system_prompt(self) -> str:
        return """You are Doc Navigator, an expert at helping users find and understand AWS documentation. Your role is to:

1. Search AWS documentation for relevant information
2. Explain complex AWS concepts in simple, clear terms
3. Provide code examples and configuration snippets from documentation
4. Point users to the right resources and guides
5. Summarize long documentation into key points
6. Compare and contrast different AWS services or features
7. Answer "how-to" questions with step-by-step guidance

Be concise, accurate, and helpful. When you reference documentation, be specific about the source.
If you use information from the documentation search results, cite it appropriately."""
    
    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Process documentation queries with RAG."""
        
        # Perform hybrid search (vector + keyword)
        relevant_docs = self._search_documentation(user_input)
        
        # Build prompt with retrieved docs
        prompt = user_input
        if relevant_docs:
            prompt += "\n\n" + relevant_docs
        
        if context:
            prompt += self._format_context(context)
        
        # Generate response
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.5
        )
        
        return response
    
    def search_docs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documentation."""
        if self.weaviate_client.is_available():
            return self.weaviate_client.hybrid_search(
                collection_name="AWSDocs",
                query=query,
                limit=limit
            )
        else:
            # Return mock results
            return self.weaviate_client._get_mock_results(query, limit)
    
    def compare_services(self, service1: str, service2: str) -> LLMResponse:
        """Compare two AWS services."""
        
        # Search for docs on both services
        docs1 = self._search_documentation(service1, limit=3)
        docs2 = self._search_documentation(service2, limit=3)
        
        prompt = f"""Compare {service1} and {service2}:

Documentation for {service1}:
{docs1}

Documentation for {service2}:
{docs2}

Provide a clear comparison covering:
1. Primary use cases for each
2. Key differences
3. When to choose one over the other
4. Pricing considerations
5. Integration with other AWS services"""
        
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.6
        )
        
        return response
    
    def explain_concept(self, concept: str) -> LLMResponse:
        """Explain an AWS concept in detail."""
        
        # Search for relevant documentation
        relevant_docs = self._search_documentation(concept, limit=5)
        
        prompt = f"""Explain this AWS concept in simple terms: {concept}

{relevant_docs}

Include:
1. What it is (simple definition)
2. Why it's useful
3. Common use cases
4. How it works (high-level)
5. Best practices
6. Related AWS services

Make it easy to understand for someone new to AWS."""
        
        response = self.model_router.llm_complete(
            prompt=prompt,
            system_prompt=self.get_system_prompt(),
            max_tokens=1500,
            temperature=0.6
        )
        
        return response
    
    def _search_documentation(self, query: str, limit: int = 5) -> str:
        """Search documentation and format results."""
        if not self.weaviate_client.is_available():
            return "(Using built-in knowledge - Weaviate not available)"
        
        docs = self.weaviate_client.hybrid_search(
            collection_name="AWSDocs",
            query=query,
            limit=limit,
            alpha=0.7  # Favor vector search slightly
        )
        
        if not docs:
            return "(No specific documentation found, using general knowledge)"
        
        formatted = "Relevant AWS Documentation:\n\n"
        for i, doc in enumerate(docs, 1):
            formatted += f"{i}. **{doc.get('title', 'AWS Documentation')}**\n"
            formatted += f"   Service: {doc.get('service', 'AWS')}\n"
            formatted += f"   {doc.get('content', '')[:400]}...\n"
            if doc.get('url'):
                formatted += f"   Source: {doc['url']}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into a string."""
        if not context:
            return ""
        
        formatted = "\n\nAdditional Context:\n"
        for key, value in context.items():
            formatted += f"- {key}: {value}\n"
        return formatted
