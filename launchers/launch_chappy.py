#!/usr/bin/env python3
"""
Chappy GUI Launcher

Easy launcher for Chappy the Brain Cluster GUI.
"""

import subprocess
import sys
import os

def main():
    """Launch the Chappy GUI."""
    print("🧠 Starting Chappy the Brain Cluster GUI...")
    print("Make sure Ollama is running: 'ollama serve'")
    print("And you have the model: 'ollama pull llama3.2:1b'")
    print()

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gui_path = os.path.join(script_dir, "chappy_gui.py")

    # Launch streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", gui_path, "--server.headless", "true"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()