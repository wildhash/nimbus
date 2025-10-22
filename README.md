# ☁️ Nimbus Copilot

**Your personal AI DevOps team for AWS: deploy faster, understand bills, and cut costs.**

Nimbus Copilot is a Streamlit application powered by multiple specialized AI agents that help you manage your AWS infrastructure, understand documentation, analyze bills, and optimize costs.

## 🌟 Features

### Four Specialized AI Agents

1. **🛠️ Setup Buddy** - Infrastructure setup and deployment expert
   - Generate CloudFormation templates
   - Guide through AWS infrastructure setup
   - Provide deployment best practices

2. **📚 Doc Navigator** - AWS documentation expert with RAG
   - Search AWS documentation efficiently
   - Explain complex AWS concepts
   - Provide relevant code examples

3. **💰 Bill Explainer** - Billing analysis specialist
   - Break down AWS bills into understandable components
   - Explain pricing models
   - Identify cost drivers

4. **📊 Cost Optimizer** - Cost optimization expert
   - Identify optimization opportunities
   - Recommend specific cost-saving actions
   - Quantify potential savings

### Key Capabilities

- **LLM Model Router**: Friendli.ai as primary provider with AWS Bedrock fallback
- **RAG with Weaviate**: Semantic search over AWS documentation
- **Excalidraw Integration**: Generate and edit architecture diagrams
- **CloudFormation Generation**: Auto-generate infrastructure templates
- **Mock Data Support**: Test without live AWS credentials
- **Live AWS Integration**: Optional connection to AWS Cost Explorer, EC2, S3
- **Savings Meter**: Track potential monthly savings
- **Reasoning Traces**: Understand why each agent was selected
- **Provider & Latency Badges**: Monitor LLM performance

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- (Optional) AWS credentials for live data
- (Optional) Friendli.ai API token
- (Optional) Weaviate instance

### Installation

1. Clone the repository:
```bash
git clone https://github.com/wildhash/nimbus.git
cd nimbus
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys (optional for mock mode)
```

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM API Keys (optional - will use mock responses if not provided)
FRIENDLI_TOKEN=your_friendli_token_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Weaviate (optional - will use mock data if not available)
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=optional_api_key

# Application Settings
USE_MOCK_DATA=true  # Set to false to use live AWS data
DEBUG_MODE=false
```

### Mock Mode vs Live Mode

**Mock Mode (Default)**:
- No AWS credentials required
- Uses realistic mock data
- Perfect for development and testing

**Live Mode**:
- Requires AWS credentials
- Connects to real AWS Cost Explorer, EC2, S3
- Provides actual cost data and optimization recommendations

Toggle between modes using the sidebar checkbox or `USE_MOCK_DATA` environment variable.

## 📖 Usage

### Chat Interface

1. Select an agent from the sidebar or let the system auto-select based on your query
2. Type your question in the chat input
3. View the response with:
   - Agent badge showing which specialist handled your query
   - Provider badge showing LLM used (Friendli.ai or Bedrock)
   - Latency badge showing response time
   - Reasoning trace explaining agent selection

### Tools Tab

**CloudFormation Generator**:
1. Describe your infrastructure in natural language
2. Click "Generate CloudFormation Template"
3. Review and download the YAML template

**Architecture Diagram**:
1. Describe your architecture
2. Click "Generate Diagram"
3. Open in Excalidraw or download JSON

### Cost Analysis Tab

View:
- Total monthly cost
- Cost breakdown by service
- Optimization opportunities with estimated savings
- Actionable recommendations

## 🏗️ Architecture

```
nimbus/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
└── src/
    ├── agents/                     # Specialized AI agents
    │   ├── base.py                # Base agent class
    │   ├── setup_buddy.py         # Infrastructure setup agent
    │   ├── doc_navigator.py       # Documentation agent
    │   ├── bill_explainer.py      # Billing analysis agent
    │   └── cost_optimizer.py      # Cost optimization agent
    ├── models/
    │   └── router.py              # LLM model router
    ├── services/
    │   ├── rag_service.py         # Weaviate RAG service
    │   ├── aws_service.py         # AWS data service (mock/live)
    │   └── excalidraw_service.py  # Diagram generation
    ├── utils/
    │   └── cloudformation.py      # CloudFormation generator
    └── orchestrator.py            # Agent orchestration

```

## 🤖 Agent Selection Logic

The orchestrator automatically routes queries to the appropriate agent:

- **Setup Buddy**: Keywords like "setup", "deploy", "create", "cloudformation"
- **Doc Navigator**: Keywords like "how to", "what is", "explain", "documentation"
- **Bill Explainer**: Keywords like "bill", "charge", "invoice", "cost breakdown"
- **Cost Optimizer**: Keywords like "optimize", "reduce cost", "save money"

You can also manually select an agent from the sidebar.

## 🔌 LLM Provider Fallback

1. **Primary**: Friendli.ai (meta-llama-3.1-70b-instruct)
2. **Fallback**: AWS Bedrock (Claude 3 Sonnet)
3. **Mock**: Returns graceful error message if both unavailable

## 🧪 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest
```

### Code Style

```bash
# Install linting tools
pip install black flake8 mypy

# Format code
black .

# Lint
flake8 .
```

## 📝 Example Queries

**Setup Buddy**:
- "How do I create a VPC with public and private subnets?"
- "Generate a CloudFormation template for a web application"

**Doc Navigator**:
- "What is the difference between EC2 instance types?"
- "How do I set up S3 lifecycle policies?"

**Bill Explainer**:
- "Why is my EC2 bill so high this month?"
- "Explain the charges on my AWS bill"

**Cost Optimizer**:
- "How can I reduce my AWS costs?"
- "What are my top cost optimization opportunities?"

## 🛠️ Troubleshooting

**Issue**: Weaviate connection failed  
**Solution**: Application will use mock data automatically. To use Weaviate, ensure it's running on the configured URL.

**Issue**: LLM provider unavailable  
**Solution**: Application will attempt fallback provider, then return mock response. Check API credentials in `.env`.

**Issue**: AWS credentials error  
**Solution**: Set `USE_MOCK_DATA=true` in `.env` or ensure AWS credentials are configured correctly.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [LlamaIndex](https://www.llamaindex.ai/)
- LLM providers: [Friendli.ai](https://friendli.ai/) and AWS Bedrock
- Vector store: [Weaviate](https://weaviate.io/)
- Diagrams: [Excalidraw](https://excalidraw.com/)
