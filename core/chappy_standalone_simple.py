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
sys.path.insert(0, str(Path(__file__).parent.parent))

from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.llm_neuron import NeuronPool
from digital_cortex.memory_palace import MemoryManager, MemorySystem
from digital_cortex.sensorium import Sensorium
from digital_cortex.amygdala import Amygdala
from digital_cortex.frontal_lobe import FrontalLobe
from digital_cortex.feedback.learner import WeightLearner
from digital_cortex.learning_center import VideoLearningContainer
from digital_cortex.rag_memory import ChappyRAGMemory, WebSearchTool, VideoUnderstandingTool

class ChappyBrain:
    """Enhanced brain class with RAG memory system."""

    def __init__(self):
        """Initialize Chappy's brain components."""
        self.colosseum = None
        self.neuron_pool = None
        self.memory_palace = None
        self.sensorium = None
        self.amygdala = None
        self.frontal_lobe = None
        self.learner = None
        self.video_learning = None
        self.thought_history = []
        self.current_state = "sleeping"
        self.reasoning_paths = []
        self.decision_history = []

        # Initialize RAG memory system
        self.rag_memory = None
        self.web_search = None
        self.video_tool = None

        # Initialize RAG components
        self._initialize_rag_system()

        # Initialize RAG components
        self._initialize_rag_system()

    def _initialize_rag_system(self):
        """Initialize the RAG memory system and tools."""
        try:
            # Initialize RAG memory
            self.rag_memory = ChappyRAGMemory(persist_directory="./chappy_memory")

            # Initialize web search tool
            self.web_search = WebSearchTool()

            # Initialize video understanding tool
            self.video_tool = VideoUnderstandingTool()

            print("🧠 RAG Memory System initialized successfully")
        except Exception as e:
            print(f"⚠️  RAG Memory System initialization failed: {e}")
            print("Chappy will work with limited memory capabilities")

    async def process_input_async(self, user_input):
        """Process user input asynchronously with RAG memory."""
        try:
            # Check for video URLs
            if self._contains_video_url(user_input):
                return await self._handle_video_request(user_input)

            # Check for web search requests
            if self._should_search_web(user_input):
                return await self._handle_web_search(user_input)

            # Retrieve relevant memories for context
            context_memories = []
            if self.rag_memory:
                context_memories = self.rag_memory.retrieve_relevant_memories(
                    user_input, n_results=3
                )

            # Build context from memories
            context = self._build_context_from_memories(context_memories)

            # Generate response using neuron pool
            if self.neuron_pool and len(self.neuron_pool.neurons) > 0:
                neuron = list(self.neuron_pool.neurons.values())[0]

                # Create enhanced prompt with context
                enhanced_prompt = self._create_enhanced_prompt(user_input, context)
                response = await neuron.process_async(enhanced_prompt)
                response_content = response.content if hasattr(response, 'content') else str(response)

                # Store conversation in RAG memory
                if self.rag_memory:
                    self.rag_memory.store_conversation(user_input, response_content)

                return response_content
            else:
                return "Hello! I'm Chappy, but my brain isn't fully initialized yet. Please wait a moment for me to wake up!"
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def _contains_video_url(self, text: str) -> bool:
        """Check if text contains a video URL."""
        import re
        video_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
            r'youtube\.com/embed/',
            r'vimeo\.com/',
            r'tiktok\.com/'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in video_patterns)

    def _should_search_web(self, text: str) -> bool:
        """Check if user is requesting a web search."""
        search_keywords = [
            'search for', 'look up', 'find information about',
            'what is', 'who is', 'how to', 'tell me about'
        ]
        return any(keyword in text.lower() for keyword in search_keywords)

    async def _handle_video_request(self, user_input: str) -> str:
        """Handle video-related requests."""
        if not self.video_tool:
            return "I can't view videos directly, but I'd love to hear about it! What happens in the video? 🎥"

        # Extract URL from input
        import re
        url_match = re.search(r'https?://[^\s]+', user_input)
        if url_match:
            url = url_match.group(0)
            response = self.video_tool.handle_video_request(url)

            # Store video interaction in memory
            if self.rag_memory:
                self.rag_memory.store_conversation(
                    user_input,
                    response,
                    {"interaction_type": "video_request", "url": url}
                )

            return response
        else:
            return "I see you're asking about a video, but I couldn't find a URL in your message. Could you share the video link?"

    async def _handle_web_search(self, user_input: str) -> str:
        """Handle web search requests."""
        if not self.web_search:
            return "I'm sorry, but web search is not available right now. I'll try to help with what I know!"

        try:
            # Extract search query
            query = self._extract_search_query(user_input)

            # Perform search
            search_results = self.web_search.search(query, max_results=3)

            if not search_results:
                return f"I couldn't find information about '{query}' online. Let me try to help with what I know instead."

            # Store search results in memory
            if self.rag_memory:
                self.rag_memory.search_web_and_store(query, search_results)

            # Format response
            response = f"I searched for '{query}' and found some information:\n\n"
            for i, result in enumerate(search_results[:3], 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   {result['snippet'][:200]}...\n"
                response += f"   Source: {result['url']}\n\n"

            response += "Would you like me to search for something more specific?"

            # Store conversation
            if self.rag_memory:
                self.rag_memory.store_conversation(
                    user_input,
                    response,
                    {"interaction_type": "web_search", "query": query}
                )

            return response

        except Exception as e:
            return f"I tried to search for information, but encountered an error: {str(e)}"

    def _extract_search_query(self, user_input: str) -> str:
        """Extract search query from user input."""
        # Remove common prefixes
        prefixes_to_remove = [
            'search for', 'look up', 'find information about',
            'tell me about', 'what is', 'who is', 'how to'
        ]

        query = user_input.lower()
        for prefix in prefixes_to_remove:
            if query.startswith(prefix):
                return user_input[len(prefix):].strip()

        # If no prefix found, return the whole input
        return user_input.strip()

    def _build_context_from_memories(self, memories: list) -> str:
        """Build context string from retrieved memories."""
        if not memories:
            return ""

        context_parts = []
        for memory in memories[:3]:  # Limit to top 3 memories
            content = memory.get('content', '')
            score = memory.get('similarity_score', 0)
            if score > 0.05:  # Include memories with any reasonable relevance
                context_parts.append(f"Previous conversation: {content}")

        return "\n".join(context_parts)

    def _create_enhanced_prompt(self, user_input: str, context: str) -> str:
        """Create an enhanced prompt with context."""
        if not context:
            return user_input

        enhanced_prompt = f"""Based on our previous conversations:

{context}

Current user message: {user_input}

Please respond naturally, referencing our conversation history when relevant."""

        return enhanced_prompt

    def process_input(self, user_input):
        """Process user input through Chappy's brain (synchronous wrapper)."""
        try:
            # Run async processing in new event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_input_async(user_input))
            loop.close()
            return result
        except Exception as e:
            return f"Sorry, I encountered an error processing your message: {str(e)}"

# Set appearance
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class ChappyDesktopApp:
    """Simple desktop application for Chappy AI."""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🧠 Chappy AI")
        self.root.geometry("900x750")  # Increased height for additional input area
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

        # Data input area (second text box)
        self.setup_data_input_area()

        # Status at very bottom
        self.setup_status_area()

        # Bind Enter key to send (Ctrl+Enter for multi-line)
        self.root.bind('<Control-Return>', lambda e: self.send_message())
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())

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

        # Chat display - read-only
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            insertbackground="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            padx=10,
            pady=10,
            state="disabled"  # Make it read-only
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
        input_frame = ctk.CTkFrame(self.main_frame, height=120)  # Increased height for multi-line input
        input_frame.pack(fill="x")
        input_frame.pack_propagate(False)

        # Input field - now multi-line
        self.message_entry = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            insertbackground="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            padx=10,
            pady=10,
            height=3  # 3 lines visible
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        # Placeholder text for multi-line input
        self.message_entry.insert("1.0", "Type your message to Chappy...")
        self.message_entry.bind("<FocusIn>", self._clear_placeholder)
        self.message_entry.bind("<FocusOut>", self._restore_placeholder)

        # Send button
        self.send_button = ctk.CTkButton(
            input_frame,
            text="📤 Send",
            width=80,
            height=60,  # Taller button to match input height
            command=self.send_message
        )
        self.send_button.pack(side="right", padx=(0, 10), pady=10)

        # Initially disable input until brain is ready
        self.message_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")

        # Set initial placeholder color
        self.message_entry.configure(fg="#888888")

    def setup_data_input_area(self):
        """Setup a second input area for data/commands."""
        data_frame = ctk.CTkFrame(self.main_frame, height=100)
        data_frame.pack(fill="x", pady=(5, 10))
        data_frame.pack_propagate(False)

        # Data input label
        data_label = ctk.CTkLabel(
            data_frame,
            text="📊 Data/Command Input",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        data_label.pack(pady=(5, 2))

        # Data input field
        self.data_entry = scrolledtext.ScrolledText(
            data_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ffffff",
            fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            insertbackground="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000",
            padx=8,
            pady=8,
            height=2  # 2 lines visible
        )
        self.data_entry.pack(fill="x", padx=10, pady=(0, 5))

        # Placeholder for data input
        self.data_entry.insert("1.0", "Enter URLs, commands, or data here...")
        self.data_entry.bind("<FocusIn>", self._clear_data_placeholder)
        self.data_entry.bind("<FocusOut>", self._restore_data_placeholder)
        self.data_entry.configure(fg="#888888")

        # Process data button
        self.process_data_button = ctk.CTkButton(
            data_frame,
            text="⚡ Process",
            width=80,
            height=30,
            command=self.process_data_input
        )
        self.process_data_button.pack(pady=(0, 5))

        # Initially disable data input until brain is ready
        self.data_entry.configure(state="disabled")
        self.process_data_button.configure(state="disabled")

    def _clear_data_placeholder(self, event):
        """Clear placeholder text when user focuses on data input."""
        if self.data_entry.get("1.0", "end-1c") == "Enter URLs, commands, or data here...":
            self.data_entry.delete("1.0", tk.END)
            self.data_entry.configure(fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000")

    def _restore_data_placeholder(self, event):
        """Restore placeholder text if data input is empty."""
        if not self.data_entry.get("1.0", "end-1c").strip():
            self.data_entry.insert("1.0", "Enter URLs, commands, or data here...")
            self.data_entry.configure(fg="#888888")

    def process_data_input(self):
        """Process data/command input."""
        if not self.is_brain_active:
            self.add_message("system", "Chappy's brain is still waking up. Please wait a moment...")
            return

        data = self.data_entry.get("1.0", "end-1c").strip()
        if not data or data == "Enter URLs, commands, or data here...":
            return

        # Add to chat as a special data message
        self.add_message("system", f"📊 Processing data: {data}")
        self.data_entry.delete("1.0", tk.END)

        # Show processing indicator
        self.status_label.configure(text="⚡ Processing data...")
        self.process_data_button.configure(state="disabled")

        # Process data in background
        def process_data():
            try:
                # For now, just echo back - can be extended for specific data processing
                response = f"I received your data/command: '{data}'. I'm processing it now..."
                self.add_message("chappy", response)
            except Exception as e:
                self.add_message("system", f"Oops! Error processing data: {str(e)}")
            finally:
                self.status_label.configure(text="✅ Ready!")
                self.process_data_button.configure(state="normal")

        threading.Thread(target=process_data, daemon=True).start()

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

        # Temporarily enable to insert text
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, formatted, msg_type)
        self.chat_display.see(tk.END)
        self.chat_display.configure(state="disabled")

        # Store in history
        self.message_history.append({
            "type": msg_type,
            "content": content,
            "timestamp": timestamp
        })

    def _clear_placeholder(self, event):
        """Clear placeholder text when user focuses on input."""
        if self.message_entry.get("1.0", "end-1c") == "Type your message to Chappy...":
            self.message_entry.delete("1.0", tk.END)
            self.message_entry.configure(fg="#ffffff" if ctk.get_appearance_mode() == "Dark" else "#000000")

    def _restore_placeholder(self, event):
        """Restore placeholder text if input is empty."""
        if not self.message_entry.get("1.0", "end-1c").strip():
            self.message_entry.insert("1.0", "Type your message to Chappy...")
            self.message_entry.configure(fg="#888888")

    def send_message(self):
        """Send a message to Chappy."""
        if not self.is_brain_active:
            self.add_message("system", "Chappy's brain is still waking up. Please wait a moment...")
            return

        message = self.message_entry.get("1.0", "end-1c").strip()
        if not message or message == "Type your message to Chappy...":
            return

        # Add user message
        self.add_message("user", message)
        self.message_entry.delete("1.0", tk.END)  # Clear the input

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
                self.brain = ChappyBrain()

                # Initialize components asynchronously
                asyncio.run(self._async_init_brain())

                self.is_brain_active = True
                self.status_label.configure(text="✅ Chappy is ready to chat!")

                # Enable input
                self.message_entry.configure(state="normal")
                self.send_button.configure(state="normal")
                self.data_entry.configure(state="normal")
                self.process_data_button.configure(state="normal")

                # Add ready message
                self.add_message("system", "Hi! I'm ready to chat. What would you like to talk about?")

            except Exception as e:
                self.status_label.configure(text="❌ Brain initialization failed")
                self.add_message("system", f"Sorry, I had trouble waking up my brain: {str(e)}")

        self.brain_thread = threading.Thread(target=init_brain, daemon=True)
        self.brain_thread.start()

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

    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = ChappyDesktopApp()
    app.run()


if __name__ == "__main__":
    main()