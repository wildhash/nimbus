"""
Nimbus Copilot - Streamlit Application
Your personal AI DevOps team for AWS
"""
import streamlit as st
import os
from dotenv import load_dotenv
import json

# Import services and agents
from src.models.router import ModelRouter
from src.orchestrator import AgentOrchestrator
from src.services.rag_service import RAGService, get_seed_documents
from src.services.aws_service import get_aws_service
from src.services.excalidraw_service import ExcalidrawService
from src.utils.cloudformation import CloudFormationGenerator

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nimbus Copilot",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    .setup-badge { background-color: #e3f2fd; color: #1976d2; }
    .docs-badge { background-color: #f3e5f5; color: #7b1fa2; }
    .bills-badge { background-color: #fff3e0; color: #e65100; }
    .optimize-badge { background-color: #e8f5e9; color: #2e7d32; }
    .provider-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        background-color: #f0f0f0;
        color: #333;
        margin-left: 0.5rem;
    }
    .latency-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        background-color: #e0e0e0;
        color: #333;
        margin-left: 0.3rem;
    }
    .savings-meter {
        background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .reasoning-box {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state."""
    if "model_router" not in st.session_state:
        st.session_state.model_router = ModelRouter()
    
    if "rag_service" not in st.session_state:
        st.session_state.rag_service = RAGService()
        # Seed with initial documents
        st.session_state.rag_service.seed_data(get_seed_documents())
    
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = AgentOrchestrator(
            st.session_state.model_router,
            st.session_state.rag_service
        )
    
    if "aws_service" not in st.session_state:
        use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
        st.session_state.aws_service = get_aws_service(use_mock)
    
    if "excalidraw_service" not in st.session_state:
        st.session_state.excalidraw_service = ExcalidrawService()
    
    if "cfn_generator" not in st.session_state:
        st.session_state.cfn_generator = CloudFormationGenerator()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "total_savings" not in st.session_state:
        st.session_state.total_savings = 0


def render_header():
    """Render the application header."""
    st.markdown('<div class="main-header">☁️ Nimbus Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Your personal AI DevOps team for AWS: deploy faster, understand bills, and cut costs</div>',
        unsafe_allow_html=True
    )


def render_sidebar():
    """Render the sidebar with agent selection and info."""
    st.sidebar.title("🤖 AI Agents")
    
    # Agent selection
    agents = {
        "Auto-Select": None,
        "🛠️ Setup Buddy": "setup",
        "📚 Doc Navigator": "docs",
        "💰 Bill Explainer": "bills",
        "📊 Cost Optimizer": "optimize"
    }
    
    selected = st.sidebar.selectbox(
        "Select Agent:",
        list(agents.keys()),
        help="Choose an agent or let the system auto-select based on your query"
    )
    
    preferred_agent = agents[selected]
    
    # Show agent descriptions
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Agent Capabilities")
    
    st.sidebar.markdown("""
    **🛠️ Setup Buddy**  
    Infrastructure setup, CloudFormation, deployment
    
    **📚 Doc Navigator**  
    AWS documentation, guides, best practices
    
    **💰 Bill Explainer**  
    Understand charges, billing breakdown
    
    **📊 Cost Optimizer**  
    Cost reduction, savings recommendations
    """)
    
    # Show current savings
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 Potential Savings")
    st.sidebar.markdown(
        f'<div class="savings-meter">${st.session_state.total_savings:.2f}/month</div>',
        unsafe_allow_html=True
    )
    
    # Data source toggle
    st.sidebar.markdown("---")
    use_mock = st.sidebar.checkbox(
        "Use Mock Data",
        value=os.getenv("USE_MOCK_DATA", "true").lower() == "true",
        help="Toggle between mock data and live AWS data"
    )
    
    return preferred_agent, use_mock


def render_agent_badge(agent_name: str):
    """Render an agent badge."""
    badge_classes = {
        "setup": "setup-badge",
        "docs": "docs-badge",
        "bills": "bills-badge",
        "optimize": "optimize-badge"
    }
    
    display_names = {
        "setup": "🛠️ Setup Buddy",
        "docs": "📚 Doc Navigator",
        "bills": "💰 Bill Explainer",
        "optimize": "📊 Cost Optimizer"
    }
    
    badge_class = badge_classes.get(agent_name, "")
    display_name = display_names.get(agent_name, agent_name)
    
    return f'<span class="agent-badge {badge_class}">{display_name}</span>'


def render_metadata_badges(provider: str, latency_ms: float):
    """Render provider and latency badges."""
    provider_badge = f'<span class="provider-badge">🔌 {provider}</span>'
    latency_badge = f'<span class="latency-badge">⚡ {latency_ms:.0f}ms</span>'
    return provider_badge + latency_badge


def render_reasoning_trace(reasoning: str):
    """Render reasoning trace."""
    return f'<div class="reasoning-box">💭 <strong>Reasoning:</strong> {reasoning}</div>'


def render_chat_interface(preferred_agent: str):
    """Render the main chat interface."""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                # Show agent badge
                st.markdown(
                    render_agent_badge(metadata.get("agent", "")),
                    unsafe_allow_html=True
                )
                
                # Show provider and latency badges
                st.markdown(
                    render_metadata_badges(
                        metadata.get("provider", "Unknown"),
                        metadata.get("latency_ms", 0)
                    ),
                    unsafe_allow_html=True
                )
                
                # Show reasoning trace
                if "reasoning" in metadata:
                    st.markdown(
                        render_reasoning_trace(metadata["reasoning"]),
                        unsafe_allow_html=True
                    )
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about AWS..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with orchestrator
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.orchestrator.process_query(
                    prompt,
                    preferred_agent=preferred_agent
                )
                
                # Display response
                st.markdown(result["response"])
                
                # Display metadata
                st.markdown(
                    render_agent_badge(result.get("agent", "")),
                    unsafe_allow_html=True
                )
                st.markdown(
                    render_metadata_badges(
                        result.get("provider", "Unknown"),
                        result.get("latency_ms", 0)
                    ),
                    unsafe_allow_html=True
                )
                st.markdown(
                    render_reasoning_trace(result.get("reasoning", "")),
                    unsafe_allow_html=True
                )
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "metadata": result
                })


def render_tools_tab():
    """Render the tools tab with CloudFormation and Excalidraw."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏗️ CloudFormation Generator")
        
        infra_desc = st.text_area(
            "Describe your infrastructure:",
            placeholder="e.g., I need a VPC with EC2 instances and an RDS database",
            height=150
        )
        
        if st.button("Generate CloudFormation Template"):
            if infra_desc:
                with st.spinner("Generating template..."):
                    template = st.session_state.cfn_generator.generate_from_description(infra_desc)
                    
                    st.code(template, language="yaml")
                    
                    # Download button
                    st.download_button(
                        label="Download Template",
                        data=template,
                        file_name="cloudformation-template.yaml",
                        mime="text/yaml"
                    )
            else:
                st.warning("Please describe your infrastructure first")
    
    with col2:
        st.subheader("🎨 Architecture Diagram")
        
        arch_desc = st.text_area(
            "Describe your architecture:",
            placeholder="e.g., Web application with load balancer, EC2 instances, and RDS",
            height=150
        )
        
        if st.button("Generate Diagram"):
            if arch_desc:
                with st.spinner("Generating diagram..."):
                    diagram = st.session_state.excalidraw_service.generate_diagram(arch_desc)
                    
                    # Show diagram JSON
                    st.json(diagram, expanded=False)
                    
                    # Excalidraw URL
                    url = st.session_state.excalidraw_service.get_embed_url(diagram)
                    st.markdown(f"[Open in Excalidraw]({url})")
                    
                    # Download button
                    diagram_json = json.dumps(diagram, indent=2)
                    st.download_button(
                        label="Download Diagram JSON",
                        data=diagram_json,
                        file_name="architecture-diagram.json",
                        mime="application/json"
                    )
            else:
                st.warning("Please describe your architecture first")


def render_cost_analysis_tab():
    """Render the cost analysis tab."""
    st.subheader("💰 Cost Analysis & Optimization")
    
    # Get cost data
    cost_data = st.session_state.aws_service.get_cost_breakdown()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Monthly Cost", f"${cost_data['total_cost']:.2f}")
        
        st.markdown("#### Cost by Service")
        for service, cost in cost_data['services'].items():
            st.write(f"**{service}**: ${cost:.2f}")
    
    with col2:
        st.markdown("#### Optimization Opportunities")
        opportunities = st.session_state.aws_service.get_optimization_opportunities()
        
        total_savings = sum(opp['estimated_savings'] for opp in opportunities)
        st.session_state.total_savings = total_savings
        
        st.metric("Potential Monthly Savings", f"${total_savings:.2f}")
        
        for opp in opportunities[:3]:
            with st.expander(f"💡 {opp['title']} - Save ${opp['estimated_savings']:.2f}"):
                st.write(f"**Description:** {opp['description']}")
                st.write(f"**Difficulty:** {opp['difficulty']}")
                st.write(f"**Action:** {opp['action']}")


def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    preferred_agent, use_mock = render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🛠️ Tools", "📊 Cost Analysis"])
    
    with tab1:
        render_chat_interface(preferred_agent)
    
    with tab2:
        render_tools_tab()
    
    with tab3:
        render_cost_analysis_tab()


if __name__ == "__main__":
    main()
