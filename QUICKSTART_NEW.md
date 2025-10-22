# 🚀 Nimbus Copilot - Quick Start Guide

Get up and running with Nimbus Copilot in 5 minutes!

## Option 1: Mock Mode (Recommended for First-Time Users)

**Perfect for:** Testing, development, and exploring features without any credentials

```bash
# 1. Clone the repository
git clone https://github.com/wildhash/nimbus.git
cd nimbus

# 2. Install core dependencies only
pip install streamlit pandas pyyaml python-dotenv

# 3. Set mock mode (or skip - it's the default!)
export USE_MOCK_DATA=true

# 4. Run the app
streamlit run app.py
```

That's it! Open http://localhost:8501 and start using Nimbus Copilot with realistic mock data.

### What Works in Mock Mode

✅ **All 4 AI agents** - Returns helpful mock responses  
✅ **Cost Analysis** - Uses `mock_data/aws_bill.json` (~$1,247/month with $366 savings opportunities)  
✅ **RAG Search** - Uses 10 curated AWS documentation stubs  
✅ **Excalidraw Diagrams** - Generates and saves diagrams locally  
✅ **CloudFormation** - Generates templates from diagrams  
✅ **All UI Features** - Badges, reasoning traces, citations  

### Mock Data Files

- `mock_data/aws_bill.json` - Sample AWS bill with optimization opportunities
- `src/services/rag_service.py` - Curated documentation stubs
- `mock_data/diagrams/` - Saved Excalidraw boards

## Option 2: Live Mode (LLM Providers Only)

**Perfect for:** Getting real AI responses while using mock AWS data

```bash
# 1. Clone and install
git clone https://github.com/wildhash/nimbus.git
cd nimbus
pip install streamlit pandas pyyaml python-dotenv

# 2. Configure environment
cp .env.example .env

# Edit .env and add ONLY your LLM API keys:
# USE_FRIENDLI=1
# FRIENDLI_TOKEN=your_friendli_token_here
# Or configure AWS Bedrock credentials for fallback

# 3. Keep mock AWS data
# USE_MOCK_DATA=true  # (default)

# 4. Run the app
streamlit run app.py
```

The app will use:
- **LLM**: Friendli.ai (fast) → AWS Bedrock (fallback) → Mock (if both unavailable)
- **AWS Data**: Mock bill and cost data
- **RAG**: Curated documentation stubs

## Option 3: Full Live Mode

**Perfect for:** Production use with real AWS account data

```bash
# 1. Clone and install
git clone https://github.com/wildhash/nimbus.git
cd nimbus
pip install streamlit pandas pyyaml python-dotenv boto3

# 2. Configure environment
cp .env.example .env

# Edit .env with your credentials:
# USE_MOCK_DATA=false
# FRIENDLI_TOKEN=your_friendli_token_here
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# AWS_REGION=us-east-1
# BEDROCK_REGION=us-east-1

# 3. Run the app
streamlit run app.py

# 4. Toggle "Live Cost Explorer" in the Cost Analysis tab
```

**Note**: Live mode requires AWS IAM permissions. See README.md "Security & IAM" section for minimal policy.

## Option 4: Complete Setup with Weaviate

**Perfect for:** Maximum performance with semantic search over AWS docs

```bash
# 1. Start Weaviate
docker run -d -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  semitechnologies/weaviate:latest

# 2. Clone and install
git clone https://github.com/wildhash/nimbus.git
cd nimbus
pip install streamlit pandas pyyaml python-dotenv weaviate-client

# 3. Initialize Weaviate
python scripts/weaviate_schema.py
python scripts/seed_min_docs.py

# 4. Configure environment
cp .env.example .env
# Edit .env with:
# WEAVIATE_URL=http://localhost:8080

# 5. Run the app
streamlit run app.py
```

Now you have the full experience with semantic search over AWS documentation!

## Toggling Between Mock and Live

### In the UI
- Use the **sidebar checkbox** "Use Mock Data"
- Costs tab has **"Live Cost Explorer"** toggle

### In .env
```bash
# Mock mode (default)
USE_MOCK_DATA=true

# Live mode
USE_MOCK_DATA=false
```

### Testing Both Modes
```bash
# Test mock mode
export USE_MOCK_DATA=true
streamlit run app.py

# Test live mode (in another terminal)
export USE_MOCK_DATA=false
streamlit run app.py
```

## First Steps in the App

### 1. Setup Buddy 🛠️
Try asking:
- "Create a web app with EC2 and RDS"
- "Deploy a serverless API"
- "Setup a VPC with public and private subnets"

### 2. Bill Explainer 💰
Check out:
- The cost summary sidebar
- Ask "Explain my AWS bill"
- Ask "Why is EC2 so expensive?"

### 3. Cost Optimizer 📊
- Click "Get Detailed Recommendations"
- View the savings meter
- See idle instances and optimization opportunities

### 4. Doc Navigator 📚
- Use the quick search buttons
- Ask "What's the difference between ALB and NLB?"
- Ask "How do S3 lifecycle policies work?"

## Verify Installation

Run the tests to make sure everything works:

```bash
# Test model router fallback
python tests/test_router_policy.py

# Test cost optimizer
python tests/test_optimizer_rules.py

# Test diagram conversion
python tests/test_convert_board_to_cfn.py

# Test core functionality
python test_core.py
```

All tests should pass ✅

## Troubleshooting

**Can't connect to Weaviate?**
- The app will automatically use mock data
- Weaviate is optional for basic functionality

**LLM provider errors?**
- Set `USE_MOCK_DATA=true` in `.env`
- Check your API keys are correct
- The app will fall back to mock responses

**Module not found?**
```bash
pip install -r requirements.txt
```

## What's Next?

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation
2. Explore each tab in the UI
3. Try both mock and live AWS data modes
4. Check out the cost optimizer recommendations
5. Customize agents for your use case

## Getting Help

- **Issues**: https://github.com/wildhash/nimbus/issues
- **Documentation**: See ARCHITECTURE.md
- **Examples**: Check the demo flows in README.md

Happy optimizing! 🚀
