#!/usr/bin/env python3
"""
Chappy Desktop App Launcher

A simple desktop launcher that starts Chappy's Streamlit server
and opens it in the default web browser.
"""

import os
import sys
import time
import subprocess
import signal
import webbrowser
from pathlib import Path

class ChappyDesktopApp:
    """Simple desktop app that launches Chappy in browser."""

    def __init__(self):
        self.streamlit_process = None
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / "venv"
        self.gui_file = self.project_dir / "chappy_gui.py"

    def start_streamlit_server(self):
        """Start the Streamlit server in the background."""
        try:
            # Activate virtual environment and start streamlit
            cmd = [
                str(self.venv_dir / "bin" / "python"),
                "-m", "streamlit", "run",
                str(self.gui_file),
                "--server.port", "8501",
                "--server.address", "127.0.0.1",
                "--server.headless", "true",
                "--server.runOnSave", "false"
            ]

            print("🧠 Starting Chappy's brain server...")
            self.streamlit_process = subprocess.Popen(
                cmd,
                cwd=str(self.project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )

            # Wait for server to start
            time.sleep(3)

            # Check if process is still running
            if self.streamlit_process.poll() is None:
                print("✅ Chappy's brain server is running!")
                return True
            else:
                stdout, stderr = self.streamlit_process.communicate()
                print(f"❌ Failed to start Streamlit server: {stderr.decode()}")
                return False

        except Exception as e:
            print(f"❌ Error starting Streamlit server: {e}")
            return False

    def stop_streamlit_server(self):
        """Stop the Streamlit server."""
        if self.streamlit_process:
            try:
                # Kill the entire process group
                os.killpg(os.getpgid(self.streamlit_process.pid), signal.SIGTERM)
                self.streamlit_process.wait(timeout=5)
                print("🛑 Chappy's brain server stopped.")
            except Exception as e:
                print(f"Warning: Could not cleanly stop server: {e}")
                try:
                    self.streamlit_process.kill()
                except:
                    pass

    def open_browser(self):
        """Open Chappy in the default web browser."""
        url = "http://127.0.0.1:8501"
        print(f"🌐 Opening Chappy in your browser: {url}")
        webbrowser.open(url)

    def run(self):
        """Run the desktop app."""
        print("🧠 Starting Chappy Desktop Application...")
        print("This may take a few moments to initialize Chappy's brain...")

        # Check if we're in the right directory
        if not Path("chappy_gui.py").exists():
            print("❌ Error: chappy_gui.py not found. Please run from the brain-cluster-ai directory.")
            sys.exit(1)

        # Check if virtual environment exists
        if not Path("venv").exists():
            print("❌ Error: Virtual environment not found. Please run setup first.")
            sys.exit(1)

        # Check if Ollama is running
        try:
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️  Warning: Ollama doesn't appear to be running.")
                print("   Please start Ollama with: ollama serve")
                print("   And ensure you have: ollama pull llama3.2:1b")
        except:
            pass

        # Start Streamlit server
        if not self.start_streamlit_server():
            print("Failed to start Chappy. Exiting.")
            return

        # Open in browser
        self.open_browser()

        print("🎉 Chappy is now running in your browser!")
        print("💡 Tip: Chappy will auto-prompt himself after 60 seconds of inactivity")
        print("Press Ctrl+C to stop Chappy")

        try:
            # Keep running until user interrupts
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down Chappy...")
            self.stop_streamlit_server()

def main():
    """Main entry point."""
    app = ChappyDesktopApp()
    app.run()

if __name__ == "__main__":
    main()