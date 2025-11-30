#!/usr/bin/env python3
"""
Chappy AI Dashboard Launcher
"""

import os
import sys
import subprocess

def main():
    """Launch the Chappy observability dashboard"""
    print("📊 Starting Chappy Observability Dashboard...")
    print("Make sure the API server is running first!")
    print("Dashboard will be available in your browser")
    print()

    # Get the project root directory
    script_dir = os.path.dirname(os.path.dirname(__file__))

    # Change to project directory
    os.chdir(script_dir)

    # Add current directory to Python path for imports
    sys.path.insert(0, script_dir)

    # Run the dashboard
    try:
        subprocess.run([sys.executable, 'core/observability_dashboard.py'])
    except KeyboardInterrupt:
        print("\n👋 Chappy dashboard closed.")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1

    print("👋 Chappy dashboard closed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())