#!/usr/bin/env python3
"""
Chappy Desktop Launcher

Launches the standalone Chappy desktop application.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the Chappy desktop application."""
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    # Import and run the desktop app
    try:
        from chappy_standalone import main as run_desktop
        run_desktop()
    except ImportError as e:
        print(f"Error importing Chappy desktop: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running Chappy desktop: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()