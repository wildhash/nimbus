# 🚀 Quick Start Guide

Get Nimbus Copilot running in under 2 minutes!

## Option 1: One-Command Start (Recommended)

```bash
# Clone and run
git clone https://github.com/wildhash/nimbus.git
cd nimbus
./run.sh
```

The script will:
1. Create a virtual environment
2. Install dependencies
3. Launch the application
4. Open your browser to http://localhost:8501

## Option 2: Manual Start

```bash
# Clone repository
git clone https://github.com/wildhash/nimbus.git
cd nimbus

# Install dependencies
pip install streamlit pandas numpy plotly pyyaml python-dotenv requests boto3

# Run application
streamlit run app.py
```

## First Use

1. **No configuration needed!** The app works immediately with mock data
2. Open http://localhost:8501 in your browser
3. Start chatting with the AI agents

## Try These Example Queries

### Setup Buddy Examples
```
"How do I create a VPC with public and private subnets?"
"Generate a CloudFormation template for a web server"
"What's the best way to deploy a multi-tier application?"
```

### Doc Navigator Examples
```
"What is the difference between EC2 instance types?"
"Explain S3 storage classes"
"How do I set up auto-scaling?"
```

### Bill Explainer Examples
```
"Why is my AWS bill so high this month?"
"Explain the charges on my bill"
"What am I being charged for in S3?"
```

### Cost Optimizer Examples
```
"How can I reduce my AWS costs?"
"What are my top optimization opportunities?"
"Should I use Reserved Instances or Spot Instances?"
```

## Using the Tools Tab

### CloudFormation Generator
1. Click the **Tools** tab
2. In the left panel, describe your infrastructure:
   ```
   I need a VPC with an EC2 web server and RDS database
   ```
3. Click **Generate CloudFormation Template**
4. Download the YAML template

### Architecture Diagram
1. In the right panel, describe your architecture:
   ```
   Web application with load balancer, EC2 instances, and RDS
   ```
2. Click **Generate Diagram**
3. Click **Open in Excalidraw** to edit the diagram

## Using the Cost Analysis Tab

1. Click the **Cost Analysis** tab
2. View your monthly cost breakdown
3. Review optimization opportunities
4. See potential savings (displayed in sidebar too!)

## Adding Your API Keys (Optional)

To use real LLM providers and live AWS data:

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your keys:
   ```bash
   # For Friendli.ai LLM
   FRIENDLI_TOKEN=your_friendli_token

   # For AWS Bedrock and Cost Explorer
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=us-east-1

   # For Weaviate vector database (optional)
   WEAVIATE_URL=http://localhost:8080

   # Enable live AWS data
   USE_MOCK_DATA=false
   ```

3. Restart the application

## Troubleshooting

### "Command not found: streamlit"
```bash
pip install streamlit
```

### "Module not found: src.models"
Make sure you're in the nimbus directory:
```bash
cd nimbus
python3 -c "import sys; print(sys.path)"
```

### "Connection error" or "API key invalid"
The app will automatically fall back to mock mode. No problem!

### Weaviate not available
The app uses built-in mock documentation. Everything still works!

## Testing Without Starting the App

### Run Core Tests
```bash
python3 test_core.py
```

Expected output:
```
✓ Imports
✓ Model Router  
✓ Agents
✓ Orchestrator
✓ Services

Results: 5 passed, 0 failed
```

### Run Demo Script
```bash
python3 demo.py
```

This showcases all features:
- Agent routing
- Cost analysis
- CloudFormation generation
- Architecture diagrams
- EC2 and S3 data

## What's Next?

1. **Explore the Agents**: Try different types of queries to see how they route
2. **Generate Infrastructure**: Use the Tools tab to create CloudFormation templates
3. **Analyze Costs**: Check the Cost Analysis tab for optimization ideas
4. **Add Your Data**: Configure API keys for live AWS data
5. **Customize**: Edit agent prompts in `src/agents/` to fit your needs

## Getting Help

- 📖 Read the full README: `README.md`
- 🎨 Check UI overview: `UI_OVERVIEW.md`
- 📝 See implementation details: `IMPLEMENTATION_SUMMARY.md`
- 🐛 Found a bug? Open an issue on GitHub

## Key Features at a Glance

✅ **No setup required** - works with mock data immediately
✅ **Four specialized agents** - auto-routing based on query
✅ **Cost optimization** - identifies savings opportunities
✅ **CloudFormation generation** - from natural language
✅ **Architecture diagrams** - with Excalidraw
✅ **Smart fallback** - graceful degradation when APIs unavailable

---

**Ready to deploy faster, understand bills, and cut costs?** 🚀

Start with: `streamlit run app.py`
