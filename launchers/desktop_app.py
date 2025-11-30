#!/usr/bin/env python3
"""
Chappy AI Desktop App Launcher
"""

import os
import sys
import subprocess

def main():
    """Launch the Chappy desktop application"""
    print("🧠 Starting Chappy Desktop Application...")
    print("Make sure Ollama is running: 'ollama serve'")
    print("And you have the model: 'ollama pull llama3.2:1b'")
    print()

    # Get the project root directory
    script_dir = os.path.dirname(os.path.dirname(__file__))

    # Change to project directory
    os.chdir(script_dir)

    # Run the desktop app
    try:
        subprocess.run([sys.executable, 'core/chappy_standalone_simple.py'])
    except KeyboardInterrupt:
        print("\n👋 Chappy desktop app closed.")
    except Exception as e:
        print(f"❌ Error launching desktop app: {e}")
        return 1

    print("👋 Chappy desktop app closed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())