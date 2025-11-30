#!/bin/bash
# Chappy AI v1.0.0 Installation Script

echo "🧠 Installing Chappy AI v1.0.0..."
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# Check if Ollama is running
if ! ollama list &> /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama:"
    echo "   ollama serve"
    exit 1
fi

# Check for required models
echo "📦 Checking for required AI models..."
if ! ollama list | grep -q "llama3.2:1b"; then
    echo "📥 Downloading llama3.2:1b model (this may take a few minutes)..."
    ollama pull llama3.2:1b
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To run Chappy AI:"
echo "   cd /path/to/extracted/chappy-ai"
echo "   ./chappy-ai"
echo ""
echo "📖 For more information, visit: https://github.com/luckyduckcode/brain-cluster-ai"