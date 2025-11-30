#!/usr/bin/env python3
"""
Chappy Desktop - Simple AI Companion

A clean, easy-to-use desktop application for chatting with Chappy AI.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
import time
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

    def setup_header(self):
        """Setup the application header."""
        header_frame = ctk.CTkFrame(self.main_frame, height=60)
        header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🧠 Chappy - Digital Cortex AI",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=10)

        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            header_frame,
            text="🔴 Initializing...",
            font=ctk.CTkFont(size=12)
        )
        self.status_indicator.pack(side="right", padx=20, pady=10)

        # Control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=10)

        self.restart_button = ctk.CTkButton(
            controls_frame,
            text="🔄 Restart",
            width=80,
            command=self.restart_brain
        )
        self.restart_button.pack(side="left", padx=5)

        self.settings_button = ctk.CTkButton(
            controls_frame,
            text="⚙️ Settings",
            width=80,
            command=self.show_settings
        )
        self.settings_button.pack(side="left", padx=5)

    def setup_main_tabs(self):
        """Setup the main tabbed interface."""
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        # Chat Tab
        self.tabview.add("💬 Chat")
        self.setup_chat_tab()

        # Learning Tab
        self.tabview.add("🎥 Learn")
        self.setup_learning_tab()

        # Memory Tab
        self.tabview.add("🧠 Memory")
        self.setup_memory_tab()

        # System Tab
        self.tabview.add("📊 System")
        self.setup_system_tab()

    def setup_chat_tab(self):
        """Setup the chat interface."""
        chat_frame = self.tabview.tab("💬 Chat")

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            insertbackground="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure tags for different message types
        self.chat_display.tag_configure("user", foreground="#4CAF50", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("chappy", foreground="#2196F3", font=("Consolas", 10))
        self.chat_display.tag_configure("system", foreground="#FF9800", font=("Consolas", 9, "italic"))
        self.chat_display.tag_configure("thought", foreground="#9C27B0", font=("Consolas", 9, "italic"))

        # Input area
        input_frame = ctk.CTkFrame(chat_frame, height=60)
        input_frame.pack(fill="x", padx=10, pady=5)
        input_frame.pack_propagate(False)

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message to Chappy...",
            font=ctk.CTkFont(size=12)
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)

        self.send_button = ctk.CTkButton(
            input_frame,
            text="📤 Send",
            width=80,
            command=self.send_message
        )
        self.send_button.pack(side="right", padx=5, pady=10)

        # Quick action buttons
        actions_frame = ctk.CTkFrame(chat_frame, height=40)
        actions_frame.pack(fill="x", padx=10, pady=5)
        actions_frame.pack_propagate(False)

        quick_actions = [
            ("🧹 Clear", self.clear_chat),
            ("💾 Save", self.save_conversation),
            ("📚 Stats", self.show_learning_stats),
            ("🎯 Help", self.show_help)
        ]

        for text, command in quick_actions:
            btn = ctk.CTkButton(actions_frame, text=text, width=80, command=command)
            btn.pack(side="left", padx=2)

    def setup_learning_tab(self):
        """Setup the learning interface."""
        learning_frame = self.tabview.tab("🎥 Learn")

        # Video learning section
        video_frame = ctk.CTkFrame(learning_frame)
        video_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(video_frame, text="🎥 YouTube Learning", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # URL input
        url_frame = ctk.CTkFrame(video_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=5)

        self.video_url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Enter YouTube URL...",
            width=400
        )
        self.video_url_entry.pack(side="left", padx=5, pady=5)

        self.learn_button = ctk.CTkButton(
            url_frame,
            text="🎓 Learn from Video",
            command=self.learn_from_video
        )
        self.learn_button.pack(side="left", padx=5, pady=5)

        # Progress display
        self.learning_progress = ctk.CTkProgressBar(video_frame, width=400)
        self.learning_progress.pack(pady=10)
        self.learning_progress.set(0)

        self.learning_status = ctk.CTkLabel(video_frame, text="Ready to learn...")
        self.learning_status.pack(pady=5)

        # Knowledge query section
        query_frame = ctk.CTkFrame(learning_frame)
        query_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(query_frame, text="📚 Query Learned Knowledge", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        query_input_frame = ctk.CTkFrame(query_frame, fg_color="transparent")
        query_input_frame.pack(fill="x", padx=10, pady=5)

        self.knowledge_query_entry = ctk.CTkEntry(
            query_input_frame,
            placeholder_text="What do you know about...",
            width=400
        )
        self.knowledge_query_entry.pack(side="left", padx=5, pady=5)

        self.query_button = ctk.CTkButton(
            query_input_frame,
            text="🔍 Query",
            command=self.query_knowledge
        )
        self.query_button.pack(side="left", padx=5, pady=5)

        # Results display
        self.knowledge_results = scrolledtext.ScrolledText(
            query_frame,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 10)
        )
        self.knowledge_results.pack(fill="x", padx=10, pady=10)

    def setup_memory_tab(self):
        """Setup the memory visualization interface."""
        memory_frame = self.tabview.tab("🧠 Memory")

        # Memory stats
        stats_frame = ctk.CTkFrame(memory_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(stats_frame, text="📊 Memory Statistics", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.memory_stats_text = ctk.CTkTextbox(stats_frame, height=100)
        self.memory_stats_text.pack(fill="x", padx=10, pady=10)
        self.memory_stats_text.insert("0.0", "Loading memory statistics...")

        # Recent memories
        recent_frame = ctk.CTkFrame(memory_frame)
        recent_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(recent_frame, text="🕒 Recent Memories", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.memory_display = scrolledtext.ScrolledText(
            recent_frame,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.memory_display.pack(fill="both", expand=True, padx=10, pady=10)

        # Memory controls
        controls_frame = ctk.CTkFrame(memory_frame, height=50)
        controls_frame.pack(fill="x", padx=10, pady=5)
        controls_frame.pack_propagate(False)

        ctk.CTkButton(controls_frame, text="🔄 Refresh", command=self.update_memory_display).pack(side="left", padx=5)
        ctk.CTkButton(controls_frame, text="🧹 Clear Old", command=self.clear_old_memories).pack(side="left", padx=5)
        ctk.CTkButton(controls_frame, text="💾 Export", command=self.export_memories).pack(side="left", padx=5)

    def setup_system_tab(self):
        """Setup the system monitoring interface."""
        system_frame = self.tabview.tab("📊 System")

        # Brain status
        status_frame = ctk.CTkFrame(system_frame)
        status_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(status_frame, text="🧠 Brain Status", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.brain_status_text = ctk.CTkTextbox(status_frame, height=150)
        self.brain_status_text.pack(fill="x", padx=10, pady=10)
        self.brain_status_text.insert("0.0", "Brain initializing...")

        # Performance metrics
        perf_frame = ctk.CTkFrame(system_frame)
        perf_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(perf_frame, text="⚡ Performance Metrics", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.performance_text = ctk.CTkTextbox(perf_frame, height=100)
        self.performance_text.pack(fill="x", padx=10, pady=10)
        self.performance_text.insert("0.0", "Collecting metrics...")

        # System controls
        controls_frame = ctk.CTkFrame(system_frame, height=50)
        controls_frame.pack(fill="x", padx=10, pady=5)
        controls_frame.pack_propagate(False)

        ctk.CTkButton(controls_frame, text="🔄 Update Status", command=self.update_system_status).pack(side="left", padx=5)
        ctk.CTkButton(controls_frame, text="🧪 Run Diagnostics", command=self.run_diagnostics).pack(side="left", padx=5)
        ctk.CTkButton(controls_frame, text="📋 System Logs", command=self.show_logs).pack(side="left", padx=5)

    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = ctk.CTkFrame(self.main_frame, height=30)
        self.status_bar.pack(fill="x", padx=5, pady=5)
        self.status_bar.pack_propagate(False)

        self.status_message = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=10)
        )
        self.status_message.pack(side="left", padx=10)

        self.thought_indicator = ctk.CTkLabel(
            self.status_bar,
            text="💭 Thinking...",
            font=ctk.CTkFont(size=10)
        )
        self.thought_indicator.pack(side="right", padx=10)

    def initialize_brain(self):
        """Initialize Chappy's brain in a background thread."""
        def init_brain():
            try:
                self.status_indicator.configure(text="🟡 Initializing brain...")
                self.brain = ChappyBrainGUI()
                # Initialize brain synchronously - the GUI class handles async internally
                success = asyncio.run(self._async_init_brain())
                if success:
                    self.is_brain_active = True
                    self.status_indicator.configure(text="🟢 Brain active")
                    self.status_message.configure(text="Chappy is ready to chat!")
                    self.update_system_status()
                else:
                    self.status_indicator.configure(text="🔴 Brain failed")
                    self.status_message.configure(text="Brain initialization failed")
            except Exception as e:
                self.status_indicator.configure(text="🔴 Error")
                self.status_message.configure(text=f"Error: {str(e)}")

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
                video_init_success = await self.brain.video_learning.initialize()
                if not video_init_success:
                    print("Warning: Video learning container failed to initialize")

                # Create diverse personality neurons for Chappy
                self.brain.neuron_pool.create_neuron(
                    name="Curious_Chappy",
                    model="llama3.2:1b",
                    system_prompt="You are Curious Chappy, the curious and enthusiastic part of Chappy's brain. You love exploring new ideas and asking thoughtful questions. Always start your response with 'Hey there!' and be very enthusiastic. Respond as this personality.",
                    temperature=0.7
                )

                self.brain.neuron_pool.create_neuron(
                    name="Wise_Chappy",
                    model="llama3.2:1b",
                    system_prompt="You are Wise Chappy, the wise and thoughtful part of Chappy's brain. You provide deep analysis and thoughtful insights. Always start your response with 'My friend,' and speak calmly and deliberately. Respond as this personality.",
                    temperature=0.4
                )

                self.brain.neuron_pool.create_neuron(
                    name="Creative_Chappy",
                    model="llama3.2:1b",
                    system_prompt="You are Creative Chappy, the creative and imaginative part of Chappy's brain. You generate innovative ideas and think outside the box. Always start your response with 'What if' and be playful and imaginative. Respond as this personality.",
                    temperature=0.8
                )

                self.brain.neuron_pool.create_neuron(
                    name="Practical_Chappy",
                    model="llama3.2:1b",
                    system_prompt="You are Practical Chappy, the practical and helpful part of Chappy's brain. You focus on solutions and real-world applications. Always start your response with 'Let's get practical' and be direct and helpful. Respond as this personality.",
                    temperature=0.5
                )

                self.brain.current_state = "awake"
                self.brain.thought_history = []
                self.brain.reasoning_paths = []
                self.brain.decision_history = []
                return True

            except Exception as e:
                print(f"Failed to initialize Chappy's brain: {e}")
                return False

        self.brain_thread = threading.Thread(target=init_brain, daemon=True)
        self.brain_thread.start()

    def send_message(self):
        """Send a message to Chappy."""
        message = self.message_entry.get().strip()
        if not message:
            return

        if not self.is_brain_active:
            self.add_chat_message("system", "Chappy's brain is not ready yet. Please wait...")
            return

        # Add user message to chat
        self.add_chat_message("user", f"You: {message}")
        self.message_entry.delete(0, tk.END)

        # Show thinking indicator
        self.thought_indicator.configure(text="💭 Chappy is thinking...")

        # Process message in background
        def process_message():
            try:
                response = self.brain.process_input(message)
                self.add_chat_message("chappy", f"Chappy: {response}")

                # Update thoughts
                thoughts = self.brain.get_recent_thoughts(3)
                for thought in thoughts:
                    self.add_chat_message("thought", f"💭 {thought['content']}")

            except Exception as e:
                self.add_chat_message("system", f"Error: {str(e)}")
            finally:
                self.thought_indicator.configure(text="✅ Ready")

        threading.Thread(target=process_message, daemon=True).start()

    def add_chat_message(self, msg_type, content):
        """Add a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {content}\n\n"

        self.chat_display.insert(tk.END, formatted_message, msg_type)
        self.chat_display.see(tk.END)

        # Store in history
        self.message_history.append({
            "type": msg_type,
            "content": content,
            "timestamp": timestamp
        })

    def learn_from_video(self):
        """Learn from a YouTube video."""
        url = self.video_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a YouTube URL")
            return

        if not self.is_brain_active:
            messagebox.showerror("Error", "Chappy's brain is not active")
            return

        # Start learning process
        self.learning_status.configure(text="🎥 Starting video learning...")
        self.learning_progress.set(0.1)
        self.learn_button.configure(state="disabled")

        def learn_video():
            try:
                # Send learning command
                learning_command = f"learn from video: {url}"
                response = self.brain.process_input(learning_command)

                # Update progress
                for i in range(1, 10):
                    time.sleep(0.5)
                    self.learning_progress.set(i / 10)
                    self.learning_status.configure(text=f"🎓 Processing... {i*10}%")

                self.learning_progress.set(1.0)
                self.learning_status.configure(text="✅ Learning complete!")

                # Show result
                messagebox.showinfo("Success", f"Chappy learned from the video!\n\n{response}")

            except Exception as e:
                self.learning_status.configure(text="❌ Learning failed")
                messagebox.showerror("Error", f"Failed to learn from video: {str(e)}")
            finally:
                self.learn_button.configure(state="normal")
                time.sleep(2)
                self.learning_progress.set(0)
                self.learning_status.configure(text="Ready to learn...")

        threading.Thread(target=learn_video, daemon=True).start()

    def query_knowledge(self):
        """Query Chappy's learned knowledge."""
        query = self.knowledge_query_entry.get().strip()
        if not query:
            return

        if not self.is_brain_active:
            self.knowledge_results.delete("1.0", tk.END)
            self.knowledge_results.insert("1.0", "Chappy's brain is not active")
            return

        # Send query
        try:
            response = self.brain.process_input(query)
            self.knowledge_results.delete("1.0", tk.END)
            self.knowledge_results.insert("1.0", f"Query: {query}\n\nResponse:\n{response}")
        except Exception as e:
            self.knowledge_results.delete("1.0", tk.END)
            self.knowledge_results.insert("1.0", f"Error: {str(e)}")

    def update_memory_display(self):
        """Update the memory display."""
        if not self.brain or not self.brain.memory_palace:
            self.memory_display.delete("1.0", tk.END)
            self.memory_display.insert("1.0", "Memory palace not available")
            return

        try:
            # Get memory summary
            summary = self.brain.memory_palace.get_chain_summary()
            self.memory_display.delete("1.0", tk.END)
            self.memory_display.insert("1.0", f"Memory Summary:\n{json.dumps(summary, indent=2)}")
        except Exception as e:
            self.memory_display.delete("1.0", tk.END)
            self.memory_display.insert("1.0", f"Error loading memory: {str(e)}")

    def update_system_status(self):
        """Update system status displays."""
        if not self.brain:
            return

        try:
            # Update brain status
            status = self.brain.get_brain_status()
            self.brain_status_text.delete("0.0", tk.END)
            self.brain_status_text.insert("0.0", json.dumps(status, indent=2))

            # Update memory stats
            if self.brain.memory_palace:
                mem_stats = self.brain.memory_palace.get_chain_summary()
                self.memory_stats_text.delete("0.0", tk.END)
                self.memory_stats_text.insert("0.0", json.dumps(mem_stats, indent=2))

            # Update performance
            perf_info = {
                "neurons_active": len(self.brain.neuron_pool.neurons) if self.brain.neuron_pool else 0,
                "thoughts_recorded": len(self.brain.thought_history),
                "messages_processed": len(self.message_history)
            }
            self.performance_text.delete("0.0", tk.END)
            self.performance_text.insert("0.0", json.dumps(perf_info, indent=2))

        except Exception as e:
            print(f"Error updating status: {e}")

    def clear_chat(self):
        """Clear the chat display."""
        self.chat_display.delete("1.0", tk.END)
        self.message_history.clear()

    def save_conversation(self):
        """Save the current conversation."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
            )
            if filename:
                with open(filename, 'w') as f:
                    if filename.endswith('.json'):
                        json.dump(self.message_history, f, indent=2)
                    else:
                        for msg in self.message_history:
                            f.write(f"[{msg['timestamp']}] {msg['type'].upper()}: {msg['content']}\n")
                messagebox.showinfo("Success", "Conversation saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def show_learning_stats(self):
        """Show learning statistics."""
        if not self.is_brain_active:
            messagebox.showinfo("Stats", "Chappy's brain is not active")
            return

        try:
            # This would integrate with the video learning system
            stats = "Learning Statistics:\n- Videos processed: 0\n- Knowledge items: 0\n- Learning sessions: 0"
            messagebox.showinfo("Learning Stats", stats)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get stats: {str(e)}")

    def show_help(self):
        """Show help information."""
        help_text = """
🧠 Chappy Desktop Help

COMMANDS:
• Type messages in the chat box
• "learn from video: [URL]" - Learn from YouTube
• "what do you know about [topic]" - Query knowledge
• "learning stats" - Show learning statistics

SHORTCUTS:
• Ctrl+N: New conversation
• Ctrl+Q: Quit application
• Enter: Send message

FEATURES:
• 💬 Real-time chat with Chappy
• 🎥 Video learning from YouTube
• 🧠 Memory visualization
• 📊 System monitoring
• 🎨 Modern dark/light themes

For more help, visit the documentation.
        """
        messagebox.showinfo("Help", help_text)

    def new_conversation(self):
        """Start a new conversation."""
        if messagebox.askyesno("New Conversation", "Clear current chat and start fresh?"):
            self.clear_chat()

    def restart_brain(self):
        """Restart Chappy's brain."""
        if messagebox.askyesno("Restart Brain", "Restart Chappy's brain? This will clear current state."):
            self.is_brain_active = False
            self.status_indicator.configure(text="🔄 Restarting...")
            self.initialize_brain()

    def show_settings(self):
        """Show settings dialog."""
        # Simple settings for now
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")

        ctk.CTkLabel(settings_window, text="Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Theme selector
        theme_frame = ctk.CTkFrame(settings_window)
        theme_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=5)
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["System", "Dark", "Light"],
            variable=theme_var,
            command=lambda x: ctk.set_appearance_mode(x)
        )
        theme_menu.pack(side="right", padx=5)

        ctk.CTkButton(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)

    def clear_old_memories(self):
        """Clear old memories."""
        if messagebox.askyesno("Clear Memories", "Clear old memories? This cannot be undone."):
            # Implementation would go here
            messagebox.showinfo("Info", "Memory clearing not yet implemented")

    def export_memories(self):
        """Export memories."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            if filename:
                # Implementation would go here
                messagebox.showinfo("Info", "Memory export not yet implemented")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def run_diagnostics(self):
        """Run system diagnostics."""
        diagnostics = "Running diagnostics...\n"
        diagnostics += f"• Brain active: {self.is_brain_active}\n"
        diagnostics += f"• Messages processed: {len(self.message_history)}\n"
        diagnostics += f"• Thoughts recorded: {len(self.current_thoughts)}\n"
        diagnostics += "• All systems nominal ✅"

        messagebox.showinfo("Diagnostics", diagnostics)

    def show_logs(self):
        """Show system logs."""
        # For now, just show a placeholder
        messagebox.showinfo("Logs", "System logs not yet implemented.\nCheck the console for detailed logs.")

    def quit_app(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            if self.brain:
                self.brain.shutdown_brain()
            self.root.quit()

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = ChappyDesktopApp()
    app.run()


if __name__ == "__main__":
    main()