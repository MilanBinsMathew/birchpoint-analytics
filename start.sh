#!/bin/bash

# FinOps AI Analyst - Native macOS Startup Script

echo "🚀 Starting FinOps AI Analyst (Lightweight Native Edition)..."

# Check if Ollama is installed natively
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed natively."
    echo "To run this efficiently on your Mac, please download and install Ollama from https://ollama.com/"
    echo "Once installed, start the Ollama application from your Applications folder and run this script again."
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is installed but does not appear to be running."
    echo "Please open the Ollama application from your Applications folder."
    exit 1
fi

echo "🤖 Pulling AI models via native Ollama (this leverages your M3 Pro GPU)..."
ollama pull llama3:8b

echo "🐍 Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "📁 Creating data directories..."
mkdir -p data/companies

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  source .venv/bin/activate"
echo "  chainlit run app.py"
echo ""
echo "Services running natively:"
echo "  - Ollama: http://localhost:11434"
