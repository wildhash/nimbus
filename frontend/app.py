"""
Nimbus Copilot - Frontend Application
Streamlit UI with 4 tabs: Setup Buddy, Bill Explainer, Cost Optimizer, Doc Navigator
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend components
from backend.utils.model_router import ModelRouter
from backend.utils.weaviate_client import WeaviateClient
from backend.utils.aws_clients import AWSClients
from backend.agents.llama.router import LlamaAgentRouter
from backend.agents.setup_buddy import SetupBuddyAgent
from backend.agents.bill_explainer import BillExplainerAgent
from backend.agents.cost_optimizer import CostOptimizerAgent
from backend.agents.doc_navigator import DocNavigatorAgent


# Page config
st.set_page_config(
    page_title="Nimbus Copilot",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .provider-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        background-color: #f0f2f6;
        margin-left: 0.5rem;
    }
    .savings-meter {
        background: linear-gradient(90deg, #00d4aa 0%, #00b894 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'model_router' not in st.session_state:
    st.session_state.model_router = ModelRouter()

if 'weaviate_client' not in st.session_state:
    st.session_state.weaviate_client = WeaviateClient()

if 'aws_clients' not in st.session_state:
    st.session_state.aws_clients = AWSClients()

if 'llama_router' not in st.session_state:
    st.session_state.llama_router = LlamaAgentRouter(
        model_router=st.session_state.model_router,
        weaviate_client=st.session_state.weaviate_client,
        aws_clients=st.session_state.aws_clients
    )


# Sidebar
with st.sidebar:
    st.title("☁️ Nimbus Copilot")
    st.markdown("*Your AI DevOps Assistant for AWS*")
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    
    use_turbo = st.toggle(
        "🚀 Turbo Mode (Friendli.ai)",
        value=os.getenv("USE_FRIENDLI", "1") == "1",
        help="Use Friendli.ai for faster inference"
    )
    
    use_mock_data = st.toggle(
        "📊 Mock Data",
        value=os.getenv("USE_MOCK_DATA", "true").lower() == "true",
        help="Use mock AWS data instead of live data"
    )
    
    st.divider()
    
    # Statistics
    st.subheader("📈 Statistics")
    stats = st.session_state.model_router.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Calls", stats['call_count'])
        st.metric("Friendli", stats['friendli_calls'])
    with col2:
        st.metric("Avg Latency", f"{stats.get('average_latency_ms', 0):.0f}ms")
        st.metric("Bedrock", stats['bedrock_calls'])
    
    if st.button("Reset Stats"):
        st.session_state.model_router.reset_stats()
        st.rerun()
    
    st.divider()
    
    # Agent info
    st.subheader("🤖 Agents")
    st.markdown("""
    - **Setup Buddy** - Infrastructure setup
    - **Bill Explainer** - Cost analysis
    - **Cost Optimizer** - Savings finder
    - **Doc Navigator** - Documentation
    """)


# Main content
st.title("☁️ Nimbus Copilot")
st.markdown("**Your friendly AI DevOps assistant for AWS**")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🛠️ Setup Buddy",
    "💰 Bill Explainer", 
    "📊 Cost Optimizer",
    "📚 Doc Navigator"
])

# Tab 1: Setup Buddy
with tab1:
    st.header("🛠️ Setup Buddy")
    st.markdown("*Deploy faster with AI-powered infrastructure setup*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Infrastructure Assistant")
        
        # Chat interface
        for msg in st.session_state.messages:
            if msg.get('tab') == 'setup':
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
                    if msg['role'] == 'assistant' and 'metadata' in msg:
                        st.caption(f"🤖 {msg['metadata'].get('agent_display', 'Agent')} • "
                                 f"⚡ {msg['metadata'].get('provider', 'Provider')} • "
                                 f"⏱️ {msg['metadata'].get('latency_ms', 0):.0f}ms")
        
        # Input
        if prompt := st.chat_input("Describe your infrastructure needs..."):
            # Add user message
            st.session_state.messages.append({
                'role': 'user',
                'content': prompt,
                'tab': 'setup'
            })
            
            # Get response from Setup Buddy
            agent = SetupBuddyAgent(
                model_router=st.session_state.model_router,
                weaviate_client=st.session_state.weaviate_client
            )
            response = agent.process(prompt)
            
            # Add assistant message
            st.session_state.messages.append({
                'role': 'assistant',
                'content': response.text,
                'tab': 'setup',
                'metadata': {
                    'agent_display': 'Setup Buddy',
                    'provider': response.provider,
                    'latency_ms': response.latency_ms
                }
            })
            
            st.rerun()
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("📋 Generate CloudFormation", use_container_width=True):
            st.info("Enter a description in the chat to generate a CloudFormation template")
        
        if st.button("🎨 Create Diagram", use_container_width=True):
            st.info("Describe your architecture in the chat to create a diagram")
        
        st.divider()
        
        st.subheader("Common Setups")
        if st.button("Web App + Database", use_container_width=True):
            st.session_state.messages.append({
                'role': 'user',
                'content': 'Setup a web application with a database',
                'tab': 'setup'
            })
            st.rerun()
        
        if st.button("Serverless API", use_container_width=True):
            st.session_state.messages.append({
                'role': 'user',
                'content': 'Create a serverless API with Lambda and API Gateway',
                'tab': 'setup'
            })
            st.rerun()

# Tab 2: Bill Explainer
with tab2:
    st.header("💰 Bill Explainer")
    st.markdown("*Understand your AWS costs with natural language explanations*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Billing Assistant")
        
        # Chat interface
        for msg in st.session_state.messages:
            if msg.get('tab') == 'bills':
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
                    if msg['role'] == 'assistant' and 'metadata' in msg:
                        st.caption(f"🤖 {msg['metadata'].get('agent_display', 'Agent')} • "
                                 f"⚡ {msg['metadata'].get('provider', 'Provider')} • "
                                 f"⏱️ {msg['metadata'].get('latency_ms', 0):.0f}ms")
        
        # Input
        if prompt := st.chat_input("Ask about your AWS bill..."):
            st.session_state.messages.append({
                'role': 'user',
                'content': prompt,
                'tab': 'bills'
            })
            
            agent = BillExplainerAgent(
                model_router=st.session_state.model_router,
                aws_clients=st.session_state.aws_clients,
                weaviate_client=st.session_state.weaviate_client
            )
            response = agent.process(prompt)
            
            st.session_state.messages.append({
                'role': 'assistant',
                'content': response.text,
                'tab': 'bills',
                'metadata': {
                    'agent_display': 'Bill Explainer',
                    'provider': response.provider,
                    'latency_ms': response.latency_ms
                }
            })
            
            st.rerun()
    
    with col2:
        st.subheader("Cost Summary")
        cost_data = st.session_state.aws_clients.get_cost_data()
        
        st.metric("Total Cost", f"${cost_data.get('total_cost', 0):.2f}")
        
        st.divider()
        
        st.subheader("Top Services")
        services = cost_data.get('cost_by_service', {})
        sorted_services = sorted(services.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for service, cost in sorted_services:
            st.metric(service.replace("Amazon ", ""), f"${cost:.2f}")

# Tab 3: Cost Optimizer
with tab3:
    st.header("📊 Cost Optimizer")
    st.markdown("*Find opportunities to reduce your AWS spending*")
    
    # Get savings summary
    optimizer = CostOptimizerAgent(
        model_router=st.session_state.model_router,
        aws_clients=st.session_state.aws_clients
    )
    savings = optimizer.get_savings_summary()
    
    # Savings meter
    total_savings = savings.get('total_monthly_savings', 0)
    st.markdown(f"""
    <div class="savings-meter">
        <h2 style="margin: 0;">💰 ${total_savings:.2f}/month</h2>
        <p style="margin: 0.5rem 0 0 0;">Potential Savings Identified</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Optimization categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("⚡ Idle EC2 Instances")
        st.metric("Instances Found", savings['ec2_idle_instances']['count'])
        st.metric("Monthly Savings", f"${savings['ec2_idle_instances']['monthly_savings']:.2f}")
    
    with col2:
        st.subheader("💾 Old Snapshots")
        st.metric("Snapshots Found", savings['old_snapshots']['count'])
        st.metric("Monthly Savings", f"${savings['old_snapshots']['monthly_savings']:.2f}")
    
    with col3:
        st.subheader("📦 S3 Lifecycle")
        st.metric("Buckets Found", savings['s3_lifecycle']['count'])
        st.metric("Monthly Savings", f"${savings['s3_lifecycle']['monthly_savings']:.2f}")
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Get Detailed Recommendations", use_container_width=True):
            with st.spinner("Analyzing your AWS environment..."):
                response = optimizer.analyze_optimizations()
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response.text,
                    'tab': 'optimize',
                    'metadata': {
                        'agent_display': 'Cost Optimizer',
                        'provider': response.provider,
                        'latency_ms': response.latency_ms
                    }
                })
    
    with col2:
        if st.button("💬 Ask Cost Question", use_container_width=True):
            st.info("Use the chat below to ask specific cost optimization questions")
    
    st.divider()
    
    # Chat interface
    for msg in st.session_state.messages:
        if msg.get('tab') == 'optimize':
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
                if msg['role'] == 'assistant' and 'metadata' in msg:
                    st.caption(f"🤖 {msg['metadata'].get('agent_display', 'Agent')} • "
                             f"⚡ {msg['metadata'].get('provider', 'Provider')} • "
                             f"⏱️ {msg['metadata'].get('latency_ms', 0):.0f}ms")
    
    if prompt := st.chat_input("Ask about cost optimization..."):
        st.session_state.messages.append({
            'role': 'user',
            'content': prompt,
            'tab': 'optimize'
        })
        
        response = optimizer.process(prompt)
        
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response.text,
            'tab': 'optimize',
            'metadata': {
                'agent_display': 'Cost Optimizer',
                'provider': response.provider,
                'latency_ms': response.latency_ms
            }
        })
        
        st.rerun()

# Tab 4: Doc Navigator
with tab4:
    st.header("📚 Doc Navigator")
    st.markdown("*Find and understand AWS documentation with semantic search*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Documentation Assistant")
        
        # Chat interface
        for msg in st.session_state.messages:
            if msg.get('tab') == 'docs':
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
                    if msg['role'] == 'assistant' and 'metadata' in msg:
                        st.caption(f"🤖 {msg['metadata'].get('agent_display', 'Agent')} • "
                                 f"⚡ {msg['metadata'].get('provider', 'Provider')} • "
                                 f"⏱️ {msg['metadata'].get('latency_ms', 0):.0f}ms")
        
        # Input
        if prompt := st.chat_input("Ask about AWS..."):
            st.session_state.messages.append({
                'role': 'user',
                'content': prompt,
                'tab': 'docs'
            })
            
            agent = DocNavigatorAgent(
                model_router=st.session_state.model_router,
                weaviate_client=st.session_state.weaviate_client
            )
            response = agent.process(prompt)
            
            st.session_state.messages.append({
                'role': 'assistant',
                'content': response.text,
                'tab': 'docs',
                'metadata': {
                    'agent_display': 'Doc Navigator',
                    'provider': response.provider,
                    'latency_ms': response.latency_ms
                }
            })
            
            st.rerun()
    
    with col2:
        st.subheader("Quick Searches")
        
        quick_questions = [
            "What is the difference between ALB and NLB?",
            "How do I set up S3 lifecycle policies?",
            "Explain VPC subnets",
            "What are EC2 instance types?",
            "How does RDS Multi-AZ work?"
        ]
        
        for question in quick_questions:
            if st.button(question, use_container_width=True, key=f"quick_{question}"):
                st.session_state.messages.append({
                    'role': 'user',
                    'content': question,
                    'tab': 'docs'
                })
                st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem;">
    <p>Nimbus Copilot • Powered by Friendli.ai, AWS Bedrock, Weaviate, and LlamaIndex</p>
</div>
""", unsafe_allow_html=True)
