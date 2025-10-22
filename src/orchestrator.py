"""
Agent orchestrator using LlamaIndex for routing between specialized agents.
"""
from typing import Dict, Any, Optional
from src.models.router import ModelRouter, ModelResponse
from src.agents.setup_buddy import SetupBuddyAgent
from src.agents.doc_navigator import DocNavigatorAgent
from src.agents.bill_explainer import BillExplainerAgent
from src.agents.cost_optimizer import CostOptimizerAgent


class AgentOrchestrator:
    """Orchestrates multiple agents to handle user queries."""
    
    def __init__(self, model_router: ModelRouter, rag_service=None):
        self.model_router = model_router
        self.rag_service = rag_service
        
        # Initialize agents
        self.agents = {
            "setup": SetupBuddyAgent(model_router),
            "docs": DocNavigatorAgent(model_router, rag_service),
            "bills": BillExplainerAgent(model_router),
            "optimize": CostOptimizerAgent(model_router)
        }
        
        self.current_agent = None
        self.conversation_history = []
    
    def route_query(self, query: str) -> str:
        """
        Route query to the appropriate agent.
        
        Returns:
            The name of the selected agent
        """
        query_lower = query.lower()
        
        # Simple keyword-based routing
        # In production, this would use LlamaIndex's more sophisticated routing
        
        # Optimization-related keywords (check first for priority)
        if any(word in query_lower for word in [
            "optimize", "reduce cost", "reduce my cost", "save money", "cheaper",
            "expensive", "savings", "cut cost"
        ]):
            return "optimize"
        
        # Setup-related keywords
        elif any(word in query_lower for word in [
            "setup", "deploy", "create", "infrastructure", "cloudformation",
            "provision", "launch", "configure"
        ]):
            return "setup"
        
        # Billing-related keywords
        elif any(word in query_lower for word in [
            "bill", "billing", "charge", "invoice", "cost breakdown",
            "why am i charged", "understand my bill"
        ]):
            return "bills"
        
        # Documentation-related keywords
        elif any(word in query_lower for word in [
            "how to", "what is", "explain", "documentation", "docs",
            "guide", "tutorial", "learn", "difference"
        ]):
            return "docs"
        
        # Default to docs for general questions
        else:
            return "docs"
    
    def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        preferred_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the appropriate agent.
        
        Args:
            query: User query
            context: Optional context information
            preferred_agent: Force using a specific agent
            
        Returns:
            Dictionary containing response, agent used, and metadata
        """
        # Route to appropriate agent
        if preferred_agent and preferred_agent in self.agents:
            agent_name = preferred_agent
        else:
            agent_name = self.route_query(query)
        
        agent = self.agents[agent_name]
        self.current_agent = agent_name
        
        # Process query with selected agent
        response = agent.process(query, context)
        
        # Add to conversation history
        self.conversation_history.append({
            "query": query,
            "agent": agent_name,
            "response": response.text,
            "provider": response.provider,
            "latency_ms": response.latency_ms
        })
        
        return {
            "response": response.text,
            "agent": agent_name,
            "agent_display": self._get_agent_display_name(agent_name),
            "provider": response.provider,
            "model": response.model,
            "latency_ms": response.latency_ms,
            "reasoning": self._generate_reasoning(agent_name, query)
        }
    
    def _get_agent_display_name(self, agent_name: str) -> str:
        """Get display-friendly agent name."""
        display_names = {
            "setup": "Setup Buddy",
            "docs": "Doc Navigator",
            "bills": "Bill Explainer",
            "optimize": "Cost Optimizer"
        }
        return display_names.get(agent_name, agent_name)
    
    def _generate_reasoning(self, agent_name: str, query: str) -> str:
        """Generate reasoning trace for why this agent was selected."""
        reasoning_templates = {
            "setup": "Query related to infrastructure setup and deployment → routed to Setup Buddy",
            "docs": "Query seeking information or documentation → routed to Doc Navigator",
            "bills": "Query about billing and charges → routed to Bill Explainer",
            "optimize": "Query about cost optimization → routed to Cost Optimizer"
        }
        return reasoning_templates.get(agent_name, "Default routing")
    
    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
