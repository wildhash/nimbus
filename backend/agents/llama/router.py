"""
LlamaIndex Agent Router using AgentWorkflow for multi-agent orchestration.
"""
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# LlamaIndex imports (optional - graceful degradation)
try:
    from llama_index.core.agent import FunctionCallingAgent
    from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step
    from llama_index.core.tools import FunctionTool
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    # Mock classes for when LlamaIndex is not available
    class FunctionCallingAgent:
        pass
    class Workflow:
        pass
    class StartEvent:
        pass
    class StopEvent:
        pass
    def step(func):
        return func
    class FunctionTool:
        pass

from backend.utils.model_router import ModelRouter, LLMResponse
from backend.utils.weaviate_client import WeaviateClient
from backend.utils.aws_clients import AWSClients


@dataclass
class AgentResponse:
    """Response from agent with reasoning trace."""
    response: str
    agent: str
    agent_display: str
    provider: str
    model: str
    latency_ms: float
    reasoning: str
    trace: List[Dict[str, Any]]
    success: bool = True


class LlamaAgentRouter:
    """
    Router using LlamaIndex AgentWorkflow for multi-agent orchestration.
    Gracefully degrades to simple routing if LlamaIndex is not available.
    """
    
    def __init__(
        self,
        model_router: ModelRouter,
        weaviate_client: Optional[WeaviateClient] = None,
        aws_clients: Optional[AWSClients] = None
    ):
        self.model_router = model_router
        self.weaviate_client = weaviate_client or WeaviateClient()
        self.aws_clients = aws_clients or AWSClients()
        
        self.use_llamaindex = LLAMAINDEX_AVAILABLE
        
        # Agent tools
        self.tools = self._create_agent_tools()
        
        # Initialize agents
        if self.use_llamaindex:
            self.agents = self._create_llamaindex_agents()
        else:
            self.agents = self._create_simple_agents()
        
        # Reasoning trace
        self.trace = []
    
    def _create_agent_tools(self) -> Dict[str, Any]:
        """Create tools for agents to use."""
        tools = {}
        
        # Weaviate search tool
        def weaviate_search(query: str, limit: int = 5) -> str:
            """Search AWS documentation using semantic search."""
            if not self.weaviate_client.is_available():
                return "Weaviate not available. Using built-in knowledge."
            
            results = self.weaviate_client.hybrid_search(
                collection_name="AWSDocs",
                query=query,
                limit=limit
            )
            
            if not results:
                return "No relevant documentation found."
            
            formatted = "Found documentation:\n\n"
            for i, doc in enumerate(results, 1):
                formatted += f"{i}. {doc.get('title', 'AWS Docs')}\n"
                formatted += f"   {doc.get('content', '')[:300]}...\n"
                formatted += f"   Source: {doc.get('url', 'N/A')}\n\n"
            
            return formatted
        
        # Cost Explorer tool
        def get_cost_data() -> str:
            """Get AWS cost and usage data."""
            data = self.aws_clients.get_cost_data()
            
            formatted = f"Total Cost: ${data['total_cost']}\n\n"
            formatted += "Cost by Service:\n"
            for service, cost in sorted(
                data['cost_by_service'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                formatted += f"  - {service}: ${cost:.2f}\n"
            
            return formatted
        
        # EC2 optimization tool
        def find_idle_ec2() -> str:
            """Find idle or underutilized EC2 instances."""
            instances = self.aws_clients.list_idle_ec2_instances()
            
            if not instances:
                return "No idle instances found."
            
            formatted = f"Found {len(instances)} potentially idle instances:\n\n"
            total_savings = 0.0
            
            for inst in instances:
                cost = inst.get('monthly_cost', 0)
                total_savings += cost
                formatted += f"- {inst['instance_id']} ({inst['instance_type']})\n"
                formatted += f"  CPU: {inst.get('cpu_utilization', 0):.1f}%\n"
                formatted += f"  Monthly cost: ${cost:.2f}\n"
            
            formatted += f"\nPotential monthly savings: ${total_savings:.2f}"
            return formatted
        
        # S3 optimization tool
        def find_s3_opportunities() -> str:
            """Find S3 lifecycle optimization opportunities."""
            opportunities = self.aws_clients.analyze_s3_lifecycle_opportunities()
            
            if not opportunities:
                return "All S3 buckets have lifecycle policies."
            
            formatted = f"Found {len(opportunities)} S3 optimization opportunities:\n\n"
            total_savings = 0.0
            
            for opp in opportunities:
                savings = opp.get('estimated_savings', 0)
                total_savings += savings
                formatted += f"- {opp['bucket_name']}\n"
                formatted += f"  {opp['recommendation']}\n"
                formatted += f"  Est. savings: ${savings:.2f}/mo\n\n"
            
            formatted += f"Total potential savings: ${total_savings:.2f}/mo"
            return formatted
        
        # CloudFormation generation tool
        def generate_cloudformation(description: str) -> str:
            """Generate CloudFormation template from description."""
            prompt = f"""Generate a CloudFormation template in YAML format for:

{description}

Include:
- Proper resource naming and dependencies
- Security best practices
- Outputs for important resource IDs
- Comments explaining key sections"""
            
            response = self.model_router.llm_complete(
                prompt=prompt,
                system_prompt="You are an expert in AWS CloudFormation. Generate clean, production-ready templates.",
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.text
        
        # Excalidraw diagram generation tool
        def generate_diagram(description: str) -> str:
            """Generate Excalidraw diagram JSON from architecture description."""
            # Simplified version - in production would generate actual Excalidraw JSON
            return f"Diagram generated for: {description}\n(Excalidraw JSON would be generated here)"
        
        # Convert tools to FunctionTool if LlamaIndex is available
        if LLAMAINDEX_AVAILABLE:
            tools['weaviate_search'] = FunctionTool.from_defaults(fn=weaviate_search)
            tools['get_cost_data'] = FunctionTool.from_defaults(fn=get_cost_data)
            tools['find_idle_ec2'] = FunctionTool.from_defaults(fn=find_idle_ec2)
            tools['find_s3_opportunities'] = FunctionTool.from_defaults(fn=find_s3_opportunities)
            tools['generate_cloudformation'] = FunctionTool.from_defaults(fn=generate_cloudformation)
            tools['generate_diagram'] = FunctionTool.from_defaults(fn=generate_diagram)
        else:
            # Store as regular functions
            tools['weaviate_search'] = weaviate_search
            tools['get_cost_data'] = get_cost_data
            tools['find_idle_ec2'] = find_idle_ec2
            tools['find_s3_opportunities'] = find_s3_opportunities
            tools['generate_cloudformation'] = generate_cloudformation
            tools['generate_diagram'] = generate_diagram
        
        return tools
    
    def _create_llamaindex_agents(self) -> Dict[str, Any]:
        """Create LlamaIndex FunctionCallingAgents."""
        # This would use actual LlamaIndex agents in production
        # For now, return simple agents that call tools
        return {
            "setup": {
                "name": "Setup Buddy",
                "tools": ["weaviate_search", "generate_cloudformation", "generate_diagram"],
                "system_prompt": "You are Setup Buddy, an AWS infrastructure expert. Help users design and deploy infrastructure."
            },
            "bills": {
                "name": "Bill Explainer",
                "tools": ["get_cost_data", "weaviate_search"],
                "system_prompt": "You are Bill Explainer. Help users understand their AWS bills and identify cost drivers."
            },
            "optimize": {
                "name": "Cost Optimizer",
                "tools": ["find_idle_ec2", "find_s3_opportunities", "get_cost_data"],
                "system_prompt": "You are Cost Optimizer. Find opportunities to reduce AWS costs and quantify savings."
            },
            "docs": {
                "name": "Doc Navigator",
                "tools": ["weaviate_search"],
                "system_prompt": "You are Doc Navigator. Help users find and understand AWS documentation."
            }
        }
    
    def _create_simple_agents(self) -> Dict[str, Any]:
        """Create simple agents when LlamaIndex is not available."""
        return self._create_llamaindex_agents()  # Same structure
    
    def route_query(self, query: str) -> str:
        """
        Route query to the appropriate agent based on keywords.
        
        Args:
            query: User query
            
        Returns:
            Agent name
        """
        query_lower = query.lower()
        
        # Optimization-related keywords (check first)
        if any(word in query_lower for word in [
            "optimize", "reduce cost", "save money", "cheaper",
            "expensive", "savings", "cut cost", "idle", "waste"
        ]):
            self.trace.append({
                "step": "routing",
                "decision": "optimize",
                "reason": "Query contains cost optimization keywords"
            })
            return "optimize"
        
        # Setup-related keywords
        elif any(word in query_lower for word in [
            "setup", "deploy", "create", "infrastructure", "cloudformation",
            "provision", "launch", "configure", "architecture"
        ]):
            self.trace.append({
                "step": "routing",
                "decision": "setup",
                "reason": "Query related to infrastructure setup"
            })
            return "setup"
        
        # Billing-related keywords
        elif any(word in query_lower for word in [
            "bill", "billing", "charge", "invoice", "cost breakdown",
            "why am i charged", "understand my bill", "spending"
        ]):
            self.trace.append({
                "step": "routing",
                "decision": "bills",
                "reason": "Query about billing and charges"
            })
            return "bills"
        
        # Documentation-related keywords (default)
        else:
            self.trace.append({
                "step": "routing",
                "decision": "docs",
                "reason": "General documentation query"
            })
            return "docs"
    
    def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        preferred_agent: Optional[str] = None
    ) -> AgentResponse:
        """
        Process a query through the appropriate agent.
        
        Args:
            query: User query
            context: Optional context
            preferred_agent: Force specific agent
            
        Returns:
            AgentResponse with result and reasoning trace
        """
        # Reset trace
        self.trace = []
        
        # Route to agent
        if preferred_agent and preferred_agent in self.agents:
            agent_name = preferred_agent
            self.trace.append({
                "step": "routing",
                "decision": agent_name,
                "reason": "User-selected agent"
            })
        else:
            agent_name = self.route_query(query)
        
        agent = self.agents[agent_name]
        
        # Build context for agent
        agent_context = self._build_agent_context(agent_name, query, context)
        
        # Execute agent
        response = self._execute_agent(agent_name, agent, query, agent_context)
        
        return AgentResponse(
            response=response.text,
            agent=agent_name,
            agent_display=agent["name"],
            provider=response.provider,
            model=response.model,
            latency_ms=response.latency_ms,
            reasoning=self._format_reasoning(agent_name, query),
            trace=self.trace.copy(),
            success=response.success
        )
    
    def _build_agent_context(
        self,
        agent_name: str,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build context string for agent."""
        context_parts = []
        
        # Add relevant tool outputs to context
        if agent_name == "docs" or agent_name == "setup":
            # Search documentation
            self.trace.append({"step": "tool_call", "tool": "weaviate_search", "query": query})
            search_func = self.tools["weaviate_search"]
            if callable(search_func):
                docs = search_func(query, limit=3)
                context_parts.append(f"Relevant Documentation:\n{docs}")
        
        if agent_name == "bills" or agent_name == "optimize":
            # Get cost data
            self.trace.append({"step": "tool_call", "tool": "get_cost_data"})
            cost_func = self.tools["get_cost_data"]
            if callable(cost_func):
                cost_data = cost_func()
                context_parts.append(f"Current Costs:\n{cost_data}")
        
        if agent_name == "optimize":
            # Get optimization opportunities
            self.trace.append({"step": "tool_call", "tool": "find_idle_ec2"})
            ec2_func = self.tools["find_idle_ec2"]
            if callable(ec2_func):
                ec2_data = ec2_func()
                context_parts.append(f"EC2 Analysis:\n{ec2_data}")
            
            self.trace.append({"step": "tool_call", "tool": "find_s3_opportunities"})
            s3_func = self.tools["find_s3_opportunities"]
            if callable(s3_func):
                s3_data = s3_func()
                context_parts.append(f"S3 Analysis:\n{s3_data}")
        
        # Add user-provided context
        if context:
            context_parts.append(f"Additional Context:\n{context}")
        
        return "\n\n".join(context_parts)
    
    def _execute_agent(
        self,
        agent_name: str,
        agent: Dict[str, Any],
        query: str,
        context: str
    ) -> LLMResponse:
        """Execute agent with query and context."""
        self.trace.append({
            "step": "agent_execution",
            "agent": agent_name,
            "query": query
        })
        
        # Build full prompt
        full_prompt = query
        if context:
            full_prompt = f"{query}\n\n{context}"
        
        # Call LLM
        response = self.model_router.llm_complete(
            prompt=full_prompt,
            system_prompt=agent["system_prompt"],
            max_tokens=1500,
            temperature=0.7
        )
        
        self.trace.append({
            "step": "llm_response",
            "provider": response.provider,
            "latency_ms": response.latency_ms,
            "success": response.success
        })
        
        return response
    
    def _format_reasoning(self, agent_name: str, query: str) -> str:
        """Format reasoning trace as human-readable string."""
        reasoning_templates = {
            "setup": f"Detected infrastructure setup query → routed to Setup Buddy → retrieved AWS docs → generated response",
            "docs": f"Documentation query → routed to Doc Navigator → searched knowledge base → synthesized answer",
            "bills": f"Billing query → routed to Bill Explainer → fetched cost data → explained charges",
            "optimize": f"Cost optimization query → routed to Cost Optimizer → analyzed resources → identified savings"
        }
        return reasoning_templates.get(agent_name, "Processed query through agent pipeline")
    
    def get_trace(self) -> List[Dict[str, Any]]:
        """Get the reasoning trace."""
        return self.trace.copy()
