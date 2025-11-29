"""
Chappy the Brain Cluster - Interactive AGI GUI

A Streamlit-based interface for the Digital Cortex AGI system,
allowing Chappy to communicate his thoughts and decisions.
"""

import streamlit as st
import sys
import time
from datetime import datetime
import json
from typing import List, Dict, Any

# Add the project path
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.llm_neuron import NeuronPool
from digital_cortex.utils.message import Message
from digital_cortex.feedback.learner import WeightLearner
from digital_cortex.memory_palace import MemoryPalaceChain
from digital_cortex.sensorium import Sensorium
from digital_cortex.amygdala import Amygdala
from digital_cortex.frontal_lobe import FrontalLobe


class ChappyBrainGUI:
    """Main GUI controller for Chappy the Brain Cluster."""

    def __init__(self):
        """Initialize Chappy's brain components."""
        self.colosseum = None
        self.neuron_pool = None
        self.memory_palace = None
        self.sensorium = None
        self.amygdala = None
        self.frontal_lobe = None
        self.learner = None
        self.thought_history = []
        self.current_state = "sleeping"

    def initialize_brain(self):
        """Initialize all brain components."""
        try:
            self.colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.4)
            self.neuron_pool = NeuronPool()
            self.memory_palace = MemoryPalaceChain(room_capacity=20)
            self.sensorium = Sensorium()
            self.amygdala = Amygdala()
            self.frontal_lobe = FrontalLobe()
            self.learner = WeightLearner(storage_path="chappy_weights.json")

            # Create diverse personality neurons for Chappy
            self.neuron_pool.create_neuron(
                name="Curious_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Curious Chappy, the curious and enthusiastic part of Chappy's brain. You love exploring new ideas and asking thoughtful questions. Always start your response with 'Hey there!' and be very enthusiastic. Respond as this personality.",
                temperature=0.7
            )

            self.neuron_pool.create_neuron(
                name="Wise_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Wise Chappy, the wise and thoughtful part of Chappy's brain. You provide deep analysis and thoughtful insights. Always start your response with 'My friend,' and speak calmly and deliberately. Respond as this personality.",
                temperature=0.4
            )

            self.neuron_pool.create_neuron(
                name="Creative_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Creative Chappy, the creative and imaginative part of Chappy's brain. You generate innovative ideas and think outside the box. Always start your response with 'What if' and be playful and imaginative. Respond as this personality.",
                temperature=0.8
            )

            self.neuron_pool.create_neuron(
                name="Practical_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Practical Chappy, the practical and helpful part of Chappy's brain. You focus on solutions and real-world applications. Always start your response with 'Let's get practical' and be direct and helpful. Respond as this personality.",
                temperature=0.5
            )

            self.current_state = "awake"
            return True

        except Exception as e:
            st.error(f"Failed to initialize Chappy's brain: {e}")
            return False

    def process_input(self, user_input):
        """Process user input through Chappy's brain."""
        self.add_thought("🗣️", f"User said: '{user_input}'", "input")

        # Step 0: Memory Retrieval - Get relevant context from Memory Palace
        self.current_state = "retrieving_memories"
        relevant_memories = self.retrieve_relevant_memories(user_input, limit=5)

        if relevant_memories:
            self.add_thought("🧠", f"Retrieved {len(relevant_memories)} relevant memories for context", "memory")
            for i, memory in enumerate(relevant_memories[:3]):  # Show top 3
                self.add_thought("💭", f"Memory {i+1}: {memory['content'][:80]}... (rel: {memory['relevance_score']:.2f})", "memory")
        else:
            self.add_thought("🧠", "No relevant memories found - starting fresh", "memory")

        # Create memory context for brain regions
        memory_context = {
            "count": len(relevant_memories),
            "recent_memories": relevant_memories,
            "last_interaction": relevant_memories[0] if relevant_memories else None,
            "context_available": len(relevant_memories) > 0
        }

        # Step 1: Sensorium processing
        self.current_state = "processing_sensory"
        sensory_msg = self.sensorium.process_text(
            user_input,
            source="user_input",
            metadata={
                "input_type": "conversation",
                "timestamp": datetime.now().isoformat(),
                "memory_context": memory_context
            }
        )
        self.add_thought("👁️", f"Sensorium analyzed: {sensory_msg.content[:100]}... (with {memory_context['count']} memories)", "sensorium")

        # Step 2: Amygdala assessment
        self.current_state = "assessing_emotion"
        # Enhance amygdala message with memory context
        enhanced_sensory = Message.create(
            sensory_msg.source,
            sensory_msg.content,
            sensory_msg.confidence,
            {**sensory_msg.metadata, "memory_context": memory_context}
        )
        amygdala_msg = self.amygdala.process_message(enhanced_sensory)
        assessment = amygdala_msg.metadata.get("amygdala_assessment", {})
        self.add_thought("💭", f"Amygdala feels: threat={assessment.get('threat_level', 0):.2f}, urgency={assessment.get('urgency', 0):.2f} (context aware)", "amygdala")

        # Step 3: Add to Colosseum
        self.colosseum.add_message(amygdala_msg)

        # Step 4: Neuron processing with memory context
        self.current_state = "thinking"

        # Enhance the user input with memory context for neurons
        enhanced_prompt = user_input
        if memory_context["context_available"]:
            context_str = "\n\nCONTEXT FROM MEMORY PALACE:\n"
            for i, memory in enumerate(relevant_memories[:3]):  # Top 3 memories
                context_str += f"{i+1}. Previous: {memory['content'][:200]}...\n"
                if memory.get("outcome"):
                    context_str += f"   Outcome: {memory['outcome']}\n"
            context_str += "\nUse this context to inform your response, but focus on the current question."
            enhanced_prompt = user_input + context_str

        # Debug: Log the prompt being sent
        self.add_thought("📝", f"Enhanced prompt: {enhanced_prompt[:100]}...", "debug")

        neuron_messages = self.neuron_pool.process_parallel(enhanced_prompt)

        for msg in neuron_messages:
            self.add_thought("🧠", f"{msg.source}: {msg.content[:150]}... (memory-enhanced)", "neuron")
            self.colosseum.add_message(msg)

        # Step 5: Find consensus
        self.current_state = "finding_consensus"
        winner, metadata = self.colosseum.find_consensus()

        if winner:
            self.add_thought("🏆", f"Consensus reached: {winner.content[:100]}...", "consensus")

            # Step 6: Learning
            contributing_neurons = metadata.get('contributing_neurons', [winner.source])
            outcome_score = 0.7  # Assume positive interaction
            self.learner.update_contributing_neurons(contributing_neurons, outcome_score)

            # Step 7: Memory storage
            outcome_data = {
                "outcome_score": outcome_score,
                "contributing_neurons": contributing_neurons,
                "interaction_type": "conversation"
            }
            memory_address = self.memory_palace.store_memory(winner, outcome_data)
            self.add_thought("🧠", f"Stored memory at: {memory_address}", "memory")

            # Step 8: Executive decision (if needed) with memory context
            if assessment.get('threat_level', 0) > 0.3 or assessment.get('urgency', 0) > 0.3:
                self.current_state = "making_decision"
                actions = ["respond_normally", "ask_for_clarification", "seek_help", "end_conversation"]
                decision = self.frontal_lobe.make_executive_decision(
                    winner, assessment, sensory_msg.metadata, relevant_memories, actions
                )
                self.add_thought("🎯", f"Executive decision: {decision.decision} (memory-informed)", "executive")

            self.current_state = "ready"
            return winner.content

        self.current_state = "confused"
        return "I'm having trouble processing that. Can you rephrase?"

    def add_thought(self, icon, content, thought_type):
        """Add a thought to Chappy's thought history."""
        thought = {
            "timestamp": datetime.now().isoformat(),
            "icon": icon,
            "content": content,
            "type": thought_type
        }
        self.thought_history.append(thought)

        # Keep only last 50 thoughts
        if len(self.thought_history) > 50:
            self.thought_history = self.thought_history[-50:]

    def get_recent_thoughts(self, limit=10):
        """Get recent thoughts for display."""
        return self.thought_history[-limit:]

    def get_brain_status(self):
        """Get current brain component status."""
        status = {
            "state": self.current_state,
            "neurons": len(self.neuron_pool.neurons) if self.neuron_pool else 0,
            "memories": self.memory_palace.get_chain_summary() if self.memory_palace else {"total_memories": 0},
            "thoughts": len(self.thought_history)
        }
        return status
    def retrieve_relevant_memories(self, current_input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the current input."""
        relevant_memories = []

        if not self.memory_palace:
            return relevant_memories

        try:
            # Get recent memories from the current room
            summary = self.memory_palace.get_chain_summary()
            if summary['total_memories'] == 0:
                return relevant_memories

            # For now, get the most recent memories
            # TODO: Implement semantic similarity search
            recent_memories = []
            current_room = self.memory_palace.current_room

            # Get memories from current room (simplified approach)
            if hasattr(current_room, 'memories'):
                for coord, memory_data in list(current_room.memories.items())[-limit:]:
                    memory_info = {
                        "address": f"room_{current_room.room_id}_{coord}",
                        "content": memory_data.get("content", ""),
                        "outcome": memory_data.get("outcome_data", {}),
                        "timestamp": memory_data.get("timestamp", ""),
                        "relevance_score": 0.5  # Placeholder for future semantic matching
                    }
                    recent_memories.append(memory_info)

            # Simple keyword matching for relevance
            input_words = set(current_input.lower().split())
            for memory in recent_memories:
                memory_content = memory["content"].lower()
                memory_words = set(memory_content.split())

                # Calculate simple overlap score
                overlap = len(input_words.intersection(memory_words))
                total_words = len(input_words.union(memory_words))

                if total_words > 0:
                    relevance = overlap / total_words
                    memory["relevance_score"] = relevance

                    # Include memories with some relevance
                    if relevance > 0.1 or len(relevant_memories) < 3:  # Always include at least 3 recent memories
                        relevant_memories.append(memory)

            # Sort by relevance and return top memories
            relevant_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
            return relevant_memories[:limit]

        except Exception as e:
            self.add_thought("⚠️", f"Memory retrieval error: {e}", "system")
            return relevant_memories
        """Gracefully shut down Chappy's brain components."""
        self.add_thought("😴", "Initiating shutdown sequence...", "system")

        # Save any important state if needed
        if self.learner:
            try:
                # Could save weights to persistent storage here
                pass
            except:
                pass

        # Clear components
        self.colosseum = None
        self.neuron_pool = None
        self.memory_palace = None
        self.sensorium = None
        self.amygdala = None
        self.frontal_lobe = None
        self.learner = None

        self.current_state = "sleeping"
        self.add_thought("🌙", "Chappy's brain has been shut down. Sweet dreams!", "system")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Chappy the Brain Cluster",
        page_icon="🧠",
        layout="wide"
    )

    st.title("🧠 Chappy the Brain Cluster")
    st.markdown("*An interactive AGI brain that thinks out loud*")

    # Initialize Chappy's brain in session state
    if 'chappy' not in st.session_state:
        st.session_state.chappy = ChappyBrainGUI()

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    chappy = st.session_state.chappy

    # Sidebar with brain status
    with st.sidebar:
        st.header("🧠 Brain Status")

        if st.button("🚀 Wake Up Chappy", type="primary"):
            with st.spinner("Initializing brain components..."):
                success = chappy.initialize_brain()
                if success:
                    st.success("Chappy is awake and ready to think!")
                    chappy.add_thought("🌅", "Good morning! Chappy's brain is now online.", "system")
                else:
                    st.error("Failed to wake Chappy. Check Ollama connection.")

        if chappy.current_state != "sleeping":
            status = chappy.get_brain_status()

            st.subheader("Current State")
            state_colors = {
                "sleeping": "gray",
                "awake": "green",
                "processing_sensory": "blue",
                "assessing_emotion": "orange",
                "thinking": "purple",
                "finding_consensus": "red",
                "making_decision": "gold",
                "ready": "green",
                "confused": "red"
            }
            st.markdown(f"**{status['state'].title()}** 🟢" if status['state'] == "ready" else f"**{status['state'].title()}**")

            st.subheader("Brain Components")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Neurons", status['neurons'])
                st.metric("Total Thoughts", status['thoughts'])
            with col2:
                st.metric("Memories Stored", status['memories'].get('total_memories', 0))

            st.subheader("Recent Thoughts")
            thoughts = chappy.get_recent_thoughts(5)
            for thought in thoughts:
                st.markdown(f"{thought['icon']} {thought['content'][:50]}...")

        # Shutdown section
        st.markdown("---")
        st.subheader("🔴 Shutdown")

        if st.button("🛑 Shut Down Chappy", type="secondary"):
            # Show confirmation dialog
            if st.session_state.get('confirm_shutdown', False):
                # Actually shut down
                chappy.shutdown_brain()

                # Clear session state
                st.session_state.messages = []
                st.session_state.confirm_shutdown = False

                st.success("Chappy has been shut down successfully!")
                st.info("To completely stop the server, close this browser tab and run: `pkill -f streamlit` in your terminal.")
                st.stop()
            else:
                st.session_state.confirm_shutdown = True
                st.warning("⚠️ Are you sure you want to shut down Chappy? This will end the current session.")

        # Cancel shutdown if user clicked but didn't confirm
        if st.session_state.get('confirm_shutdown', False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Shut Down", type="primary"):
                    # This will trigger the shutdown above
                    st.rerun()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.confirm_shutdown = False
                    st.rerun()

    # Main chat interface
    st.header("💬 Talk to Chappy")

    # Check if Chappy is sleeping
    if chappy.current_state == "sleeping":
        st.info("😴 Chappy is currently sleeping. Click '🚀 Wake Up Chappy' in the sidebar to start a new session.")
        st.stop()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like Chappy to think about?"):
        if chappy.current_state == "sleeping":
            st.error("Chappy is sleeping! Click 'Wake Up Chappy' first.")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Process with Chappy's brain
            with st.chat_message("assistant"):
                with st.spinner("Chappy is thinking..."):
                    try:
                        response = chappy.process_input(prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Oops! Chappy had a brain freeze: {e}"
                        st.error(error_msg)
                        chappy.add_thought("❌", f"Error: {e}", "error")
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Live thought stream
    if chappy.current_state != "sleeping":
        st.header("🔴 Live Thought Stream")
        thoughts_container = st.empty()

        while True:
            thoughts = chappy.get_recent_thoughts(20)
            thought_display = ""
            for thought in thoughts:
                timestamp = thought['timestamp'].split('T')[1][:8]  # HH:MM:SS
                thought_display += f"**{timestamp}** {thought['icon']} {thought['content']}\n\n"

            thoughts_container.markdown(thought_display)

            # Update every 2 seconds
            time.sleep(2)

            # Break if no new thoughts for a while
            if not thoughts or (datetime.now() - datetime.fromisoformat(thoughts[-1]['timestamp'])).seconds > 10:
                break

    # Footer
    st.markdown("---")
    st.markdown("*Built with the Digital Cortex AGI framework*")
    st.markdown("*Chappy thinks with multiple brain regions: Sensorium, Amygdala, Neurons, Colosseum, Memory, and Frontal Lobe*")


if __name__ == "__main__":
    main()