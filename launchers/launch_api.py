#!/usr/bin/env python3
"""
Chappy API Launcher

Easy launcher for the Chappy Brain Cluster REST API.
"""

import subprocess
import sys
import os

def main():
    """Launch the Chappy API."""
    print("🧠 Starting Chappy Brain Cluster API...")
    print("Make sure Ollama is running: 'ollama serve'")
    print("And you have the model: 'ollama pull llama3.2:1b'")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print()

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    api_path = os.path.join(script_dir, "api.py")

    # Launch the API
    cmd = [sys.executable, api_path]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()