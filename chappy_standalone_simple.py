#!/usr/bin/env python3
"""
Chappy Desktop - Simple AI Companion

A clean, easy-to-use desktop application for chatting with Chappy AI.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import threading
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

from chappy_gui import ChappyBrainGUI
from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.llm_neuron import NeuronPool
from digital_cortex.memory_palace import MemoryManager, MemorySystem
from digital_cortex.sensorium import Sensorium
from digital_cortex.amygdala import Amygdala
from digital_cortex.frontal_lobe import FrontalLobe
from digital_cortex.feedback.learner import WeightLearner
from digital_cortex.learning_center import VideoLearningContainer

# Set appearance
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class ChappyDesktopApp:
    """Simple desktop application for Chappy AI."""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🧠 Chappy AI")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)

        # Initialize brain
        self.brain = None
        self.brain_thread = None
        self.is_brain_active = False

        # Message history
        self.message_history = []

        # Setup simple UI
        self.setup_simple_ui()

        # Initialize brain in background
        self.initialize_brain()

    def setup_simple_ui(self):
        """Setup a clean, simple interface."""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome header
        self.setup_welcome_header()

        # Chat area (takes most space)
        self.setup_chat_area()

        # Input area at bottom
        self.setup_input_area()

        # Status at very bottom
        self.setup_status_area()

        # Bind Enter key to send
        self.root.bind('<Return>', lambda e: self.send_message())

    def setup_welcome_header(self):
        """Setup a friendly welcome header."""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        # Welcome message
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="👋 Welcome to Chappy!",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        welcome_label.pack(pady=(15, 5))

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Your friendly AI companion with a brain inspired by biology",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack()

    def setup_chat_area(self):
        """Setup the main chat display area."""
        # Chat container
        chat_container = ctk.CTkFrame(self.main_frame)
        chat_container.pack(fill="both", expand=True, pady=(0, 10))

        # Chat title
        chat_title = ctk.CTkLabel(
            chat_container,
            text="💬 Chat with Chappy",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        chat_title.pack(pady=(10, 5))

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            insertbackground="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Configure message styles
        self.chat_display.tag_configure("user", foreground="#4CAF50", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_configure("chappy", foreground="#2196F3", font=("Segoe UI", 11))
        self.chat_display.tag_configure("system", foreground="#FF9800", font=("Segoe UI", 9, "italic"))

        # Add welcome message
        self.add_message("system", "Hi there! I'm Chappy, your AI companion. I'm initializing my brain right now. This might take a moment...")

    def setup_input_area(self):
        """Setup the message input area."""
        input_frame = ctk.CTkFrame(self.main_frame, height=80)
        input_frame.pack(fill="x")
        input_frame.pack_propagate(False)

        # Input field
        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message to Chappy...",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        # Send button
        self.send_button = ctk.CTkButton(
            input_frame,
            text="📤 Send",
            width=80,
            height=40,
            command=self.send_message
        )
        self.send_button.pack(side="right", padx=(0, 10), pady=10)

        # Initially disable input until brain is ready
        self.message_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")

    def setup_status_area(self):
        """Setup a simple status area."""
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="🧠 Initializing Chappy's brain...",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(pady=(5, 0))

    def add_message(self, msg_type, content):
        """Add a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M")
        if msg_type == "user":
            formatted = f"You ({timestamp}):\n{content}\n\n"
        elif msg_type == "chappy":
            formatted = f"Chappy ({timestamp}):\n{content}\n\n"
        else:  # system
            formatted = f"💭 {content}\n\n"

        self.chat_display.insert(tk.END, formatted, msg_type)
        self.chat_display.see(tk.END)

        # Store in history
        self.message_history.append({
            "type": msg_type,
            "content": content,
            "timestamp": timestamp
        })

    def send_message(self):
        """Send a message to Chappy."""
        if not self.is_brain_active:
            self.add_message("system", "Chappy's brain is still waking up. Please wait a moment...")
            return

        message = self.message_entry.get().strip()
        if not message:
            return

        # Add user message
        self.add_message("user", message)
        self.message_entry.delete(0, tk.END)

        # Show typing indicator
        self.status_label.configure(text="💭 Chappy is thinking...")
        self.send_button.configure(state="disabled")

        # Process message in background
        def process_message():
            try:
                response = self.brain.process_input(message)
                self.add_message("chappy", response)
            except Exception as e:
                self.add_message("system", f"Oops! Chappy had a little brain freeze: {str(e)}")
            finally:
                self.status_label.configure(text="✅ Ready to chat!")
                self.send_button.configure(state="normal")

        threading.Thread(target=process_message, daemon=True).start()

    def initialize_brain(self):
        """Initialize Chappy's brain in a background thread."""
        def init_brain():
            try:
                self.status_label.configure(text="🧠 Initializing Chappy's brain...")

                # Create brain instance
                self.brain = ChappyBrainGUI()

                # Initialize components asynchronously
                asyncio.run(self._async_init_brain())

                self.is_brain_active = True
                self.status_label.configure(text="✅ Chappy is ready to chat!")

                # Enable input
                self.message_entry.configure(state="normal")
                self.send_button.configure(state="normal")

                # Add ready message
                self.add_message("system", "Hi! I'm ready to chat. What would you like to talk about?")

            except Exception as e:
                self.status_label.configure(text="❌ Brain initialization failed")
                self.add_message("system", f"Sorry, I had trouble waking up my brain: {str(e)}")

        async def _async_init_brain(self):
            """Async brain initialization."""
            try:
                # Initialize components
                self.brain.colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.4)
                self.brain.neuron_pool = NeuronPool()
                self.brain.memory_palace = MemoryManager(system=MemorySystem.GRAPH, max_nodes=5000)
                self.brain.sensorium = Sensorium()
                self.brain.amygdala = Amygdala()
                self.brain.frontal_lobe = FrontalLobe()
                self.brain.learner = WeightLearner(storage_path="chappy_weights.json")

                # Initialize video learning container
                self.brain.video_learning = VideoLearningContainer(
                    corpus_colosseum=self.brain.colosseum,
                    memory_palace=self.brain.memory_palace
                )
                # Initialize video learning if possible
                try:
                    video_init_success = await self.brain.video_learning.initialize()
                    if not video_init_success:
                        print("Video learning initialization failed, but continuing...")
                except Exception as e:
                    print(f"Video learning init error: {e}")

                # Create personality neurons
                personalities = [
                    ("Curious_Chappy", "You are Curious Chappy, very enthusiastic and loves asking questions. Start with 'Hey there!'"),
                    ("Wise_Chappy", "You are Wise Chappy, thoughtful and deliberate. Start with 'My friend,'"),
                    ("Creative_Chappy", "You are Creative Chappy, imaginative and playful. Start with 'What if'"),
                    ("Practical_Chappy", "You are Practical Chappy, direct and helpful. Start with 'Let's get practical'")
                ]

                for name, prompt in personalities:
                    self.brain.neuron_pool.create_neuron(
                        name=name,
                        model="llama3.2:1b",
                        system_prompt=prompt,
                        temperature=0.7
                    )

                self.brain.current_state = "awake"
                self.brain.thought_history = []
                self.brain.reasoning_paths = []
                self.brain.decision_history = []

            except Exception as e:
                print(f"Failed to initialize Chappy's brain: {e}")
                raise

        self.brain_thread = threading.Thread(target=init_brain, daemon=True)
        self.brain_thread.start()

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = ChappyDesktopApp()
    app.run()


if __name__ == "__main__":
    main()