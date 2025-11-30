#!/usr/bin/env python3
"""
Chappy AI - Main Version Selector Launcher
Choose which version of Chappy to run
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json

class ChappyLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chappy AI Launcher")
        self.root.geometry("500x400")
        self.root.configure(bg='#2b2b2b')

        # Get available versions
        self.versions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'versions')
        self.versions = self.get_available_versions()

        self.setup_ui()

    def get_available_versions(self):
        """Get list of available Chappy versions"""
        versions = []
        if os.path.exists(self.versions_dir):
            for item in os.listdir(self.versions_dir):
                if os.path.isdir(os.path.join(self.versions_dir, item)) and item.startswith('v'):
                    versions.append(item)
        return sorted(versions, reverse=True)

    def setup_ui(self):
        """Setup the launcher UI"""
        # Title
        title_label = tk.Label(self.root, text="🧠 Chappy AI Launcher",
                              font=("Arial", 20, "bold"), bg='#2b2b2b', fg='white')
        title_label.pack(pady=20)

        # Version selection
        version_frame = tk.Frame(self.root, bg='#2b2b2b')
        version_frame.pack(pady=10)

        version_label = tk.Label(version_frame, text="Select Version:",
                                bg='#2b2b2b', fg='white', font=("Arial", 12))
        version_label.pack()

        self.version_var = tk.StringVar()
        if self.versions:
            self.version_var.set(self.versions[0])

        version_combo = ttk.Combobox(version_frame, textvariable=self.version_var,
                                    values=self.versions, state="readonly", width=20)
        version_combo.pack(pady=5)

        # Launch options
        options_frame = tk.Frame(self.root, bg='#2b2b2b')
        options_frame.pack(pady=20)

        # Desktop App Button
        desktop_btn = tk.Button(options_frame, text="🖥️  Desktop App",
                               command=self.launch_desktop, bg='#4a90e2', fg='white',
                               font=("Arial", 12, "bold"), width=15, height=2)
        desktop_btn.pack(side=tk.LEFT, padx=10)

        # API Server Button
        api_btn = tk.Button(options_frame, text="🌐 API Server",
                           command=self.launch_api, bg='#50c878', fg='white',
                           font=("Arial", 12, "bold"), width=15, height=2)
        api_btn.pack(side=tk.LEFT, padx=10)

        # Dashboard Button
        dash_btn = tk.Button(options_frame, text="📊 Dashboard",
                            command=self.launch_dashboard, bg='#ff6b6b', fg='white',
                            font=("Arial", 12, "bold"), width=15, height=2)
        dash_btn.pack(side=tk.LEFT, padx=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", bg='#2b2b2b', fg='yellow')
        self.status_label.pack(pady=10)

    def launch_desktop(self):
        """Launch desktop application"""
        version = self.version_var.get()
        if not version:
            messagebox.showerror("Error", "Please select a version")
            return

        self.status_label.config(text=f"Launching Desktop App (v{version[1:]})...")
        self.root.update()

        try:
            # Import and run the desktop app for selected version
            version_path = os.path.join(self.versions_dir, version)
            sys.path.insert(0, version_path)

            # For now, just run the current desktop app
            # Later versions can have their own implementations
            subprocess.Popen([sys.executable, 'core/chappy_standalone_simple.py'])

            self.status_label.config(text="Desktop App launched successfully!")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Launch Error", f"Failed to launch desktop app:\n{str(e)}")

    def launch_api(self):
        """Launch API server"""
        version = self.version_var.get()
        if not version:
            messagebox.showerror("Error", "Please select a version")
            return

        self.status_label.config(text=f"Launching API Server (v{version[1:]})...")
        self.root.update()

        try:
            subprocess.Popen([sys.executable, 'launchers/launch_api.py'])
            self.status_label.config(text="API Server launched successfully!")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Launch Error", f"Failed to launch API server:\n{str(e)}")

    def launch_dashboard(self):
        """Launch observability dashboard"""
        version = self.version_var.get()
        if not version:
            messagebox.showerror("Error", "Please select a version")
            return

        self.status_label.config(text=f"Launching Dashboard (v{version[1:]})...")
        self.root.update()

        try:
            subprocess.Popen([sys.executable, 'launchers/launch_dashboard.py'])
            self.status_label.config(text="Dashboard launched successfully!")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Launch Error", f"Failed to launch dashboard:\n{str(e)}")

def main():
    launcher = ChappyLauncher()
    launcher.root.mainloop()

if __name__ == "__main__":
    main()