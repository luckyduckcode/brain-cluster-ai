#!/bin/bash
# Chappy API Launcher Script

echo "🧠 Starting Chappy Brain Cluster API..."
echo "Make sure Ollama is running: 'ollama serve'"
echo "And you have the model: 'ollama pull llama3.2:1b'"
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Launch the API
python3 "$SCRIPT_DIR/api.py"