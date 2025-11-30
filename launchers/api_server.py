#!/usr/bin/env python3
"""
Chappy AI API Server Launcher
"""

import os
import sys
import subprocess

def main():
    """Launch the Chappy API server"""
    print("🌐 Starting Chappy API Server...")
    print("API will be available at: http://localhost:8000")
    print("Documentation at: http://localhost:8000/docs")
    print()

    # Get the project root directory
    script_dir = os.path.dirname(os.path.dirname(__file__))

    # Change to project directory
    os.chdir(script_dir)

    # Add current directory to Python path for imports
    sys.path.insert(0, script_dir)

    # Run the API server
    try:
        subprocess.run([sys.executable, 'core/api.py'])
    except KeyboardInterrupt:
        print("\n👋 Chappy API server stopped.")
    except Exception as e:
        print(f"❌ Error launching API server: {e}")
        return 1

    print("👋 Chappy API server stopped.")
    return 0

if __name__ == "__main__":
    sys.exit(main())