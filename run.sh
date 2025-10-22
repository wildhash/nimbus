#!/bin/bash
# Nimbus Copilot startup script

echo "🚀 Starting Nimbus Copilot..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file. You can edit it to add your API keys."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✨ Setup complete!"
echo ""
echo "🌐 Starting Streamlit application..."
echo "   Access the app at: http://localhost:8501"
echo ""

# Run Streamlit
streamlit run app.py
