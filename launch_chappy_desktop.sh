#!/bin/bash
"""
Chappy Desktop App Launcher Script

Easy launcher for Chappy's desktop application.
"""

echo "🧠 Starting Chappy Desktop Application..."
echo "Make sure Ollama is running: 'ollama serve'"
echo "And you have the model: 'ollama pull llama3.2:1b'"
echo ""

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the desktop app
python3 "$SCRIPT_DIR/chappy_standalone_simple.py"

echo "👋 Chappy desktop app closed."