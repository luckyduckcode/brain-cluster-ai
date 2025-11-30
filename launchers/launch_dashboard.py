#!/usr/bin/env python3
"""
Launcher script for the Brain Cluster AI Observability Dashboard.
Starts the Streamlit dashboard for real-time system monitoring.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the observability dashboard."""
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()

    # Change to the project directory
    os.chdir(script_dir)

    print("🧠 Starting Brain Cluster AI Observability Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔗 Make sure the API server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the dashboard")

    try:
        # Launch Streamlit dashboard
        cmd = [sys.executable, "-m", "streamlit", "run", "observability_dashboard.py",
               "--server.port", "8501", "--server.address", "0.0.0.0"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()