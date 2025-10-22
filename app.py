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


def render_metadata_badges(provider: str, latency_ms: float, mode: str = "Live"):
    """Render provider, latency, and mode badges."""
    # Determine mode based on provider
    if provider.lower() == "mock":
        mode = "Mock"
    
    provider_badge = f'<span class="provider-badge">🔌 {provider}</span>'
    latency_badge = f'<span class="latency-badge">⚡ {latency_ms:.0f}ms</span>'
    mode_badge = f'<span class="provider-badge">📊 Mode: {mode}</span>'
    return provider_badge + latency_badge + mode_badge


def render_reasoning_trace(reasoning: str):
    """Render reasoning trace in an expander."""
    if not reasoning:
        return ""
    
    # Format reasoning as a list if it's a string
    if isinstance(reasoning, str):
        reasoning_items = [reasoning]
    elif isinstance(reasoning, list):
        reasoning_items = reasoning
    else:
        reasoning_items = [str(reasoning)]
    
    # Create expander content
    content = '<div class="reasoning-box">'
    content += '<strong>💭 Agent Reasoning:</strong><br>'
    for item in reasoning_items:
        content += f'• {item}<br>'
    content += '</div>'
    
    return content


def render_chat_interface(preferred_agent: str):
    """Render the main chat interface."""
    # Get use_mock setting
    use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    mode = "Mock" if use_mock else "Live"
    
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
                
                # Show provider, latency, and mode badges
                st.markdown(
                    render_metadata_badges(
                        metadata.get("provider", "Unknown"),
                        metadata.get("latency_ms", 0),
                        mode
                    ),
                    unsafe_allow_html=True
                )
                
                # Show reasoning trace in expander
                if "reasoning" in metadata and metadata["reasoning"]:
                    with st.expander("🔍 Show Reasoning"):
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
                        result.get("latency_ms", 0),
                        mode
                    ),
                    unsafe_allow_html=True
                )
                
                # Show reasoning in expander
                if result.get("reasoning"):
                    with st.expander("🔍 Show Reasoning"):
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
            height=150,
            key="cfn_desc"
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
        
        # Regenerate CFN from latest board
        st.markdown("---")
        st.markdown("#### Regenerate from Diagram")
        
        if st.button("🔄 Regenerate CFN from Latest Board"):
            # Check if we have a saved board
            from pathlib import Path
            manifest_path = Path("./mock_data/diagrams/manifest.json")
            
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Get latest board
                boards = manifest.get("boards", {})
                if boards:
                    # Get first board's latest version
                    first_board_key = list(boards.keys())[0]
                    latest_file = boards[first_board_key].get("latest_key")
                    
                    if latest_file:
                        board_path = Path(f"./mock_data/diagrams/{latest_file}")
                        if board_path.exists():
                            with open(board_path, 'r') as f:
                                board = json.load(f)
                            
                            # Regenerate CFN
                            cfn_template = st.session_state.excalidraw_service.board_to_cfn(board)
                            
                            st.success("✓ Regenerated from latest board")
                            st.code(cfn_template, language="yaml")
                            
                            st.download_button(
                                label="Download Regenerated Template",
                                data=cfn_template,
                                file_name="board-cloudformation.yaml",
                                mime="text/yaml",
                                key="download_regen"
                            )
                        else:
                            st.warning("Board file not found")
                    else:
                        st.info("No boards saved yet. Generate a diagram first.")
                else:
                    st.info("No boards saved yet. Generate a diagram first.")
            else:
                st.info("No boards saved yet. Generate a diagram first.")
    
    with col2:
        st.subheader("🎨 Architecture Diagram")
        
        arch_desc = st.text_area(
            "Describe your architecture:",
            placeholder="e.g., Web application with load balancer, EC2 instances, and RDS",
            height=150,
            key="arch_desc"
        )
        
        if st.button("Generate Diagram"):
            if arch_desc:
                with st.spinner("Generating diagram..."):
                    diagram = st.session_state.excalidraw_service.generate_diagram(arch_desc)
                    
                    # Save the diagram
                    save_result = st.session_state.excalidraw_service.save_board(diagram)
                    
                    if save_result.get("success"):
                        st.success(f"✓ Diagram saved: {save_result['filename']}")
                    
                    # Show diagram JSON
                    st.json(diagram, expanded=False)
                    
                    # Excalidraw URL
                    url = st.session_state.excalidraw_service.get_embed_url(diagram)
                    st.markdown(f"### [🎨 Open in Excalidraw]({url})")
                    st.info("Click the link above to edit your diagram in Excalidraw")
                    
                    # Download button
                    diagram_json = json.dumps(diagram, indent=2)
                    st.download_button(
                        label="Download Diagram JSON",
                        data=diagram_json,
                        file_name="architecture-diagram.json",
                        mime="application/json",
                        key="download_diagram"
                    )
            else:
                st.warning("Please describe your architecture first")


def render_cost_analysis_tab():
    """Render the cost analysis tab."""
    st.subheader("💰 Cost Analysis & Optimization")
    
    # Toggle for Live Cost Explorer
    col_toggle1, col_toggle2 = st.columns([3, 1])
    with col_toggle2:
        use_live_ce = st.checkbox("Live Cost Explorer", value=False, help="Use live AWS Cost Explorer data (requires AWS credentials)")
    
    # Get cost data
    if use_live_ce:
        try:
            cost_data = st.session_state.aws_service.get_cost_breakdown()
        except Exception as e:
            st.warning(f"Failed to get live cost data: {e}. Using mock data.")
            cost_data = st.session_state.aws_service.get_cost_breakdown()
    else:
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
    
    # Citations panel from RAG
    st.markdown("---")
    st.markdown("### 📚 Related Documentation")
    
    # Get relevant docs about cost optimization
    if st.session_state.rag_service:
        from src.services.rag_service import format_citations
        hits = st.session_state.rag_service.hybrid_search("AWS cost optimization best practices", k=3)
        if hits:
            citations = format_citations(hits)
            st.markdown(citations)


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
