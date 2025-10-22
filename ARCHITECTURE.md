# ☁️ Nimbus Copilot - Complete Architecture Guide

**Your personal AI DevOps team for AWS: deploy faster, understand bills, and cut costs.**

Nimbus Copilot is a production-ready Streamlit application powered by multiple specialized AI agents, LlamaIndex orchestration, Weaviate semantic search, and dual LLM providers (Friendli.ai + AWS Bedrock) for fast, intelligent AWS management.

---

## 🌟 Key Features

### Four Specialized AI Agents

1. **🛠️ Setup Buddy** - Infrastructure setup and deployment expert
   - Generate CloudFormation templates from natural language
   - Create architecture diagrams
   - Guide through AWS infrastructure setup
   - Search relevant documentation using Weaviate

2. **📚 Doc Navigator** - AWS documentation expert with RAG
   - Hybrid search (vector + keyword) over AWS docs
   - Explain complex AWS concepts in simple terms
   - Compare AWS services
   - Provide code examples and best practices

3. **💰 Bill Explainer** - Billing analysis specialist
   - Break down AWS bills into understandable components
   - Explain pricing models and charge types
   - Identify cost drivers
   - Natural language explanations of spending

4. **📊 Cost Optimizer** - Cost optimization expert
   - Identify idle EC2 instances
   - Find old EBS snapshots
   - Detect S3 buckets without lifecycle policies
   - Quantify potential savings ($/month)
   - Provide actionable optimization steps

### Advanced Capabilities

- **LLM Model Router**: Friendli.ai as primary (sub-second latency) with AWS Bedrock fallback
- **RAG with Weaviate**: Semantic + keyword hybrid search over ~150 AWS documentation chunks
- **LlamaIndex Integration**: Multi-agent orchestration with tool usage
- **Excalidraw Integration**: Convert architecture diagrams to CloudFormation
- **Mock Data Support**: Full functionality without AWS credentials
- **Live AWS Integration**: Connect to Cost Explorer, EC2, S3 for real data
- **Savings Meter**: Visual display of potential monthly savings
- **Provider Badges**: See which LLM provider handled each request
- **Latency Tracking**: Monitor response times

---

## 🏗️ Architecture

```
nimbus/
├── frontend/
│   └── app.py                      # Streamlit UI with 4 tabs
├── backend/
│   ├── agents/
│   │   ├── setup_buddy.py         # Infrastructure setup agent
│   │   ├── bill_explainer.py      # Billing analysis agent
│   │   ├── cost_optimizer.py      # Cost optimization agent
│   │   ├── doc_navigator.py       # Documentation agent with RAG
│   │   └── llama/
│   │       └── router.py          # LlamaIndex AgentWorkflow router
│   ├── utils/
│   │   ├── model_router.py        # Friendli→Bedrock fallback router
│   │   ├── friendli.py            # Friendli.ai client wrapper
│   │   ├── bedrock.py             # AWS Bedrock client wrapper
│   │   ├── weaviate_client.py     # Weaviate hybrid search client
│   │   └── aws_clients.py         # AWS service clients (CE, EC2, S3)
│   └── diagram/
│       ├── convert.py             # Excalidraw → CloudFormation
│       └── manifest.json          # Diagram metadata
├── scripts/
│   ├── weaviate_schema.py         # Initialize Weaviate schema
│   └── seed_min_docs.py           # Seed AWS documentation
├── mock_data/
│   └── aws_bill.json              # Mock billing data
├── tests/
│   ├── test_router_policy.py      # LLM router tests
│   ├── test_optimizer_rules.py    # Cost optimizer tests
│   └── test_convert_board_to_cfn.py  # Diagram conversion tests
├── infra/
│   └── iam/
│       └── policy.min.json        # Minimal IAM permissions
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- (Optional) AWS credentials for live data
- (Optional) Friendli.ai API token for fast inference
- (Optional) Weaviate instance for semantic search

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wildhash/nimbus.git
   cd nimbus
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Core dependencies (required):
   - `streamlit` - Web UI
   - `pyyaml` - CloudFormation templates
   - `python-dotenv` - Environment variables
   - `pandas`, `plotly` - Data visualization
   - `boto3` - AWS SDK

   Optional dependencies (for enhanced features):
   - `friendli` - Friendli.ai LLM provider
   - `llama-index` - Agent orchestration
   - `weaviate-client` - Vector database
   - `fastapi`, `uvicorn` - Excalidraw bridge

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional for mock mode)
   ```

4. **(Optional) Initialize Weaviate:**
   ```bash
   # Start local Weaviate
   docker run -d -p 8080:8080 semitechnologies/weaviate:latest
   
   # Initialize schema
   python scripts/weaviate_schema.py
   
   # Seed documentation
   python scripts/seed_min_docs.py
   ```

5. **Run the application:**
   ```bash
   streamlit run frontend/app.py
   ```
   
   Or using the original app:
   ```bash
   streamlit run app.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:8501`

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM Configuration
FRIENDLI_API_KEY=your_friendli_api_key_here
FRIENDLI_URL=https://api.friendli.ai/v1
FRIENDLI_MODEL=meta-llama-3.1-70b-instruct
USE_FRIENDLI=1                    # 1=enabled, 0=disabled

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
BEDROCK_REGION=us-east-1
BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Weaviate Configuration
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=optional_api_key  # For Weaviate Cloud

# Application Settings
USE_MOCK_DATA=true                 # Use mock data instead of live AWS
DEBUG_MODE=false
```

### Running Modes

**Mock Mode (Default)**:
- No AWS credentials required
- Uses realistic mock data
- Perfect for development and testing
- All features work without external dependencies

**Live Mode**:
- Requires AWS credentials with appropriate permissions
- Connects to real AWS Cost Explorer, EC2, S3
- Provides actual cost data and optimization recommendations
- See `infra/iam/policy.min.json` for required IAM permissions

**Turbo Mode**:
- Enable `USE_FRIENDLI=1` in `.env`
- Requires Friendli.ai API key
- Sub-second inference with Llama 3.1 70B
- Automatically falls back to Bedrock if unavailable

---

## 📖 Usage

### Setup Buddy Tab

1. Click on the **🛠️ Setup Buddy** tab
2. Describe your infrastructure needs in the chat
3. Get CloudFormation templates, architecture diagrams, and deployment guidance

**Example prompts:**
- "Create a web application with EC2, RDS, and S3"
- "Deploy a serverless API with Lambda and API Gateway"
- "Setup a VPC with public and private subnets"

### Bill Explainer Tab

1. Navigate to **💰 Bill Explainer**
2. View your cost summary in the sidebar
3. Ask questions about your AWS bill

**Example prompts:**
- "Why is my bill so high this month?"
- "Explain the EC2 charges"
- "What is data transfer costing me?"

### Cost Optimizer Tab

1. Open **📊 Cost Optimizer**
2. View the savings meter showing total potential savings
3. See breakdown by category (EC2, Snapshots, S3)
4. Click "Get Detailed Recommendations" for actionable steps

**Identifies:**
- Idle EC2 instances (<10% CPU utilization)
- EBS snapshots older than 90 days
- S3 buckets without lifecycle policies
- Unattached EBS volumes

### Doc Navigator Tab

1. Switch to **📚 Doc Navigator**
2. Ask questions about AWS services
3. Use quick search buttons for common questions

**Example prompts:**
- "What is the difference between ALB and NLB?"
- "How do I set up S3 lifecycle policies?"
- "Explain VPC subnets"

---

## 🧪 Testing

### Run All Tests

```bash
# Router fallback policy
python tests/test_router_policy.py

# Cost optimizer rules
python tests/test_optimizer_rules.py

# Excalidraw to CloudFormation conversion
python tests/test_convert_board_to_cfn.py

# Original core tests
python test_core.py
```

All tests pass with mock data, no AWS credentials required.

### Test Output Example

```
============================================================
Model Router Fallback Policy Tests
============================================================
✓ Router initialized successfully
✓ Correctly fell back to mock provider
✓ Statistics tracked correctly
✓ Provider preference respected

Results: 4 passed, 0 failed
```

---

## 🎨 Architecture Deep Dive

### LLM Provider Fallback

```python
ModelRouter.llm_complete()
    ↓
Try Friendli.ai (0.5s latency)
    ↓ (on failure)
Try AWS Bedrock (1.2s latency)
    ↓ (on failure)
Return mock response
```

### Agent Orchestration

```python
LlamaAgentRouter.process_query()
    ↓
Route based on keywords
    ↓
Select appropriate agent
    ↓
Gather context (Weaviate, AWS APIs)
    ↓
Execute agent with LLM
    ↓
Return response + reasoning trace
```

### Weaviate Hybrid Search

```python
WeaviateClient.hybrid_search()
    ↓
Vector search (semantic similarity)
    +
Keyword search (BM25)
    ↓
Combine results (alpha=0.5)
    ↓
Return top K documents
```

---

## 🔒 Security

### IAM Permissions

Minimal IAM policy required for live AWS mode:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ec2:DescribeInstances",
        "ec2:DescribeSnapshots",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLifecycleConfiguration",
        "cloudwatch:GetMetricStatistics",
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

Full policy: `infra/iam/policy.min.json`

### Best Practices

- Store API keys in `.env`, never commit them
- Use least-privilege IAM roles
- Enable MFA for AWS accounts
- Rotate credentials regularly
- Use Weaviate Cloud with API key authentication

---

## 📊 Performance

### Typical Response Times

- **Friendli.ai**: 300-800ms
- **AWS Bedrock**: 800-1500ms
- **Mock**: <10ms

### Weaviate Search

- **Hybrid search**: 50-200ms
- **150 documents**: ~5MB memory
- **Scales** to millions of documents

---

## 🛠️ Development

### Adding a New Agent

1. Create agent class in `backend/agents/`:
   ```python
   class MyAgent:
       def __init__(self, model_router):
           self.model_router = model_router
       
       def process(self, query, context=None):
           response = self.model_router.llm_complete(...)
           return response
   ```

2. Add to `LlamaAgentRouter` in `backend/agents/llama/router.py`

3. Create tab in `frontend/app.py`

### Adding New Tools

Add tools to `LlamaAgentRouter._create_agent_tools()`:

```python
def my_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result

tools['my_tool'] = FunctionTool.from_defaults(fn=my_tool)
```

---

## 📝 Example Workflows

### 1. Deploy a Web Application

**Setup Buddy**:
```
User: "Deploy a Python web app with a PostgreSQL database"
Agent: Generates CloudFormation with EC2, RDS, ALB, and VPC
```

### 2. Understand High Bills

**Bill Explainer**:
```
User: "Why is my data transfer cost so high?"
Agent: Analyzes bill → "89% of data transfer is cross-region traffic. 
       Consider using CloudFront CDN to reduce costs by 50%."
```

### 3. Optimize Costs

**Cost Optimizer**:
```
User: "Find cost savings opportunities"
Agent: Scans resources → "Found 3 idle instances ($231/mo), 
       2 buckets without lifecycle ($124/mo). 
       Total: $355/mo in potential savings."
```

### 4. Learn About Services

**Doc Navigator**:
```
User: "Explain the difference between ALB and NLB"
Agent: Searches docs → "ALB operates at Layer 7 (HTTP/HTTPS), 
       ideal for web apps. NLB operates at Layer 4 (TCP), 
       handles millions of requests with ultra-low latency."
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Streamlit** - Beautiful web UI framework
- **LlamaIndex** - Agent orchestration
- **Friendli.ai** - Fast LLM inference
- **AWS Bedrock** - Claude 3 Sonnet
- **Weaviate** - Vector database for RAG
- **Excalidraw** - Architecture diagrams

---

## 🐛 Troubleshooting

### Issue: "Weaviate connection failed"
**Solution**: Application will use mock data automatically. To use Weaviate:
```bash
docker run -d -p 8080:8080 semitechnologies/weaviate:latest
python scripts/weaviate_schema.py
python scripts/seed_min_docs.py
```

### Issue: "LLM provider unavailable"
**Solution**: Application will attempt fallback provider, then return mock response. Check API credentials in `.env`.

### Issue: "AWS credentials error"
**Solution**: Set `USE_MOCK_DATA=true` in `.env` or configure AWS credentials:
```bash
aws configure
# OR
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

### Issue: "Module not found"
**Solution**: Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 📞 Support

- **Issues**: https://github.com/wildhash/nimbus/issues
- **Discussions**: https://github.com/wildhash/nimbus/discussions

---

## 🗺️ Roadmap

- [ ] Excalidraw live editor integration
- [ ] Export CloudFormation templates to file
- [ ] Cost forecasting with ML models
- [ ] Multi-region cost analysis
- [ ] Slack/Teams integration for alerts
- [ ] CI/CD pipeline integration
- [ ] Custom agent creation UI
- [ ] Multi-cloud support (Azure, GCP)

---

**Built with ❤️ for the AWS community**
