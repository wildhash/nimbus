# 🚀 Nimbus Copilot - Quick Start Guide

Get up and running with Nimbus Copilot in 5 minutes!

## Option 1: Basic Setup (No External Dependencies)

**Perfect for:** Testing, development, and exploring features

```bash
# 1. Clone the repository
git clone https://github.com/wildhash/nimbus.git
cd nimbus

# 2. Install core dependencies
pip install streamlit pandas plotly pyyaml python-dotenv boto3

# 3. Run with mock data (no configuration needed!)
streamlit run frontend/app.py
```

That's it! Open http://localhost:8501 and start using Nimbus Copilot with realistic mock data.

## Option 2: Full Setup with LLM Providers

**Perfect for:** Production use with real AI responses

```bash
# 1. Clone and install
git clone https://github.com/wildhash/nimbus.git
cd nimbus
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env

# Edit .env and add your API keys:
# FRIENDLI_API_KEY=your_key_here
# AWS_ACCESS_KEY_ID=your_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_here

# 3. Run the app
streamlit run frontend/app.py
```

The app will use Friendli.ai (fast) → Bedrock (fallback) → Mock (if both unavailable)

## Option 3: Complete Setup with Semantic Search

**Perfect for:** Maximum performance with RAG capabilities

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
pip install -r requirements.txt

# 3. Initialize Weaviate
python scripts/weaviate_schema.py
python scripts/seed_min_docs.py

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the app
streamlit run frontend/app.py
```

Now you have the full experience with semantic search over AWS documentation!

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
