"""
Chappy the Brain Cluster - Enhanced Interactive AGI GUI

An advanced Streamlit-based interface for the Digital Cortex AGI system,
featuring thought visualization, confidence indicators, and interactive reasoning exploration.
"""

import streamlit as st
import sys
import time
from datetime import datetime
import json
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
from collections import defaultdict

# Add the project path
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.llm_neuron import NeuronPool
from digital_cortex.utils.message import Message
from digital_cortex.feedback.learner import WeightLearner
from digital_cortex.memory_palace import MemoryManager, MemorySystem
from digital_cortex.sensorium import Sensorium
from digital_cortex.amygdala import Amygdala
from digital_cortex.frontal_lobe import FrontalLobe
from digital_cortex.learning_center import VideoLearningContainer


class ChappyBrainGUI:
    """Enhanced GUI controller for Chappy the Brain Cluster with advanced visualization."""

    def __init__(self):
        """Initialize Chappy's brain components with enhanced tracking."""
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

        # Enhanced tracking for visualization
        self.neuron_activations = []  # Track neuron firing patterns
        self.confidence_history = []  # Track confidence over time
        self.decision_history = []    # Track major decisions
        self.reasoning_paths = []     # Track reasoning chains
        self.current_neuron_details = {}  # Detailed neuron information

    def initialize_brain(self):
        """Initialize all brain components."""
        try:
            self.colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.4)
            self.neuron_pool = NeuronPool()
            self.memory_palace = MemoryManager(system=MemorySystem.GRAPH, max_nodes=5000)
            self.sensorium = Sensorium()
            self.amygdala = Amygdala()
            self.frontal_lobe = FrontalLobe()
            self.learner = WeightLearner(storage_path="chappy_weights.json")

            # Initialize video learning container
            self.video_learning = VideoLearningContainer(
                corpus_colosseum=self.colosseum,
                memory_palace=self.memory_palace
            )
            # Note: Video learning will be initialized asynchronously when needed

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

        # Check if this is a video learning request first
        if self.video_learning:
            try:
                # Initialize video learning if not already done
                if not hasattr(self.video_learning, '_initialized'):
                    import asyncio
                    asyncio.run(self.video_learning.initialize())
                    self.video_learning._initialized = True

                video_message = Message(
                    source="user_input",
                    content=user_input.lower(),
                    confidence=1.0
                )
                video_response = asyncio.run(self.video_learning.process_message(video_message))
                if video_response:
                    self.add_thought("🎥", f"Video learning handled: {video_response.content[:100]}...", "video_learning")
                    return video_response.content
            except Exception as e:
                self.add_thought("❌", f"Video learning error: {e}", "error")

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

        # Track reasoning path
        self.reasoning_paths.append([{
            'component': 'Memory',
            'action': f'Retrieved {len(relevant_memories)} memories',
            'timestamp': datetime.now().isoformat()
        }])

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

        # Track neuron activations
        for msg in neuron_messages:
            self.add_thought("🧠", f"{msg.source}: {msg.content[:150]}... (memory-enhanced)", "neuron")
            self.colosseum.add_message(msg)

            # Track activation
            self.neuron_activations.append({
                'neuron': msg.source,
                'timestamp': datetime.now().isoformat(),
                'confidence': msg.confidence,
                'content_length': len(msg.content)
            })

            # Update reasoning path
            self.reasoning_paths[-1].append({
                'component': msg.source,
                'action': f'Generated response (conf: {msg.confidence:.2f})',
                'timestamp': datetime.now().isoformat()
            })

        # Step 5: Find consensus
        self.current_state = "finding_consensus"
        winner, metadata = self.colosseum.find_consensus()

        if winner:
            # Track confidence
            self.confidence_history.append({
                'timestamp': datetime.now().isoformat(),
                'confidence': winner.confidence,
                'source': winner.source
            })

            self.add_thought("🏆", f"Consensus reached: {winner.content[:100]}... (conf: {winner.confidence:.2f})", "consensus")

            # Update reasoning path
            self.reasoning_paths[-1].append({
                'component': 'Colosseum',
                'action': f'Consensus found with {winner.source} (conf: {winner.confidence:.2f})',
                'timestamp': datetime.now().isoformat()
            })

            # Step 6: Learning
            contributing_neurons = metadata.get('contributing_neurons', [winner.source])
            outcome_score = 0.7  # Assume positive interaction
            self.learner.update_contributing_neurons(contributing_neurons, outcome_score)

            # Update attention weights for future consensus
            for neuron in contributing_neurons:
                self.colosseum.update_neuron_performance(neuron, outcome_score)

            # Step 7: Memory storage
            outcome_data = {
                "outcome_score": outcome_score,
                "contributing_neurons": contributing_neurons,
                "interaction_type": "conversation"
            }
            memory_address = self.memory_palace.store_memory(winner, outcome_data)
            self.add_thought("🧠", f"Stored memory at: {memory_address}", "memory")

            # Update reasoning path
            self.reasoning_paths[-1].append({
                'component': 'Memory',
                'action': f'Stored outcome at {memory_address}',
                'timestamp': datetime.now().isoformat()
            })

            # Step 8: Executive decision (if needed) with memory context
            if assessment.get('threat_level', 0) > 0.3 or assessment.get('urgency', 0) > 0.3:
                self.current_state = "making_decision"
                actions = ["respond_normally", "ask_for_clarification", "seek_help", "end_conversation"]
                decision = self.frontal_lobe.make_executive_decision(
                    winner, assessment, sensory_msg.metadata, relevant_memories, actions
                )

                # Track decision
                self.decision_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'decision': decision.decision,
                    'reasoning': decision.reasoning,
                    'threat_level': assessment.get('threat_level', 0),
                    'urgency': assessment.get('urgency', 0)
                })

                self.add_thought("🎯", f"Executive decision: {decision.decision} (memory-informed)", "executive")

                # Update reasoning path
                self.reasoning_paths[-1].append({
                    'component': 'Frontal Lobe',
                    'action': f'Executive decision: {decision.decision}',
                    'timestamp': datetime.now().isoformat()
                })

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
            "thoughts": len(self.thought_history),
            "video_learning": self.video_learning.get_container_info() if self.video_learning else {"status": "not_initialized"}
        }
        return status
    def retrieve_relevant_memories(self, current_input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to the current input."""
        if not self.memory_palace:
            return []

        # Use the memory manager's retrieve method
        return self.memory_palace.retrieve_relevant_memories(current_input, limit)

    def shutdown_brain(self):
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

        # Shutdown video learning container
        if self.video_learning:
            try:
                import asyncio
                asyncio.run(self.video_learning.shutdown())
            except Exception as e:
                print(f"Error shutting down video learning: {e}")
        self.video_learning = None

        self.current_state = "sleeping"
        self.add_thought("🌙", "Chappy's brain has been shut down. Sweet dreams!", "system")

    def create_thought_graph(self):
        """Create a real-time visualization of neuron activations and thought patterns."""
        if not self.neuron_activations:
            return None

        # Create a network graph of neuron interactions
        G = nx.Graph()

        # Add nodes for neurons
        neuron_names = set()
        for activation in self.neuron_activations[-20:]:  # Last 20 activations
            neuron_names.add(activation.get('neuron', 'unknown'))

        for neuron in neuron_names:
            G.add_node(neuron, size=20, color='lightblue')

        # Add edges based on recent interactions
        recent_activations = self.neuron_activations[-10:]
        for i in range(len(recent_activations)-1):
            neuron1 = recent_activations[i].get('neuron', 'unknown')
            neuron2 = recent_activations[i+1].get('neuron', 'unknown')
            if neuron1 != neuron2:
                if G.has_edge(neuron1, neuron2):
                    G[neuron1][neuron2]['weight'] += 1
                else:
                    G.add_edge(neuron1, neuron2, weight=1)

        # Create Plotly figure
        pos = nx.spring_layout(G, seed=42)

        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_text = []
        node_size = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            node_size.append(G.degree(node) * 5 + 20)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=node_size,
                color='lightblue',
                line_width=2))

        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title="🧠 Neuron Activation Network",
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                       )
        return fig

    def create_confidence_chart(self):
        """Create a confidence trend chart over time."""
        if not self.confidence_history:
            return None

        # Prepare data for plotting
        df = pd.DataFrame(self.confidence_history[-20:])  # Last 20 confidence readings

        if df.empty:
            return None

        fig = px.line(df, x='timestamp', y='confidence',
                     title="📊 Confidence Trend",
                     labels={'confidence': 'Confidence Level', 'timestamp': 'Time'},
                     markers=True)

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Confidence (0-1)",
            yaxis_range=[0, 1]
        )

        return fig

    def create_reasoning_path_visualization(self):
        """Create a visualization of the current reasoning path."""
        if not self.reasoning_paths:
            return None

        # Get the most recent reasoning path
        current_path = self.reasoning_paths[-1] if self.reasoning_paths else []

        if not current_path:
            return None

        # Create a simple flowchart-like visualization
        steps = []
        for i, step in enumerate(current_path):
            steps.append(f"{i+1}. {step.get('component', 'Unknown')}: {step.get('action', 'Processing')}")

        # Create a text-based visualization for now (can be enhanced to graphical later)
        path_text = "🔗 Current Reasoning Path:\n\n" + "\n→ ".join(steps)

        return path_text

    def get_neuron_details(self, neuron_name):
        """Get detailed information about a specific neuron."""
        if not self.neuron_pool:
            return {}

        neuron = self.neuron_pool.neurons.get(neuron_name)
        if not neuron:
            return {}

        # Get activation history for this neuron
        activations = [a for a in self.neuron_activations if a.get('neuron') == neuron_name]

    def create_confidence_meter(self):
        """Create a real-time confidence meter widget."""
        if not self.confidence_history:
            return None

        latest_confidence = self.confidence_history[-1]['confidence']

        # Create a gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_confidence,
            title={'text': "Current Confidence"},
            gauge={
                'axis': {'range': [0, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.3], 'color': "red"},
                    {'range': [0.3, 0.7], 'color': "yellow"},
                    {'range': [0.7, 1], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': latest_confidence
                }
            }
        ))

        fig.update_layout(height=200)
        return fig


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

    if 'last_input_time' not in st.session_state:
        st.session_state.last_input_time = datetime.now()

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
                    st.session_state.last_input_time = datetime.now()  # Reset timer on wake up
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

            # Real-time confidence meter
            st.subheader("🎯 Current Confidence")
            confidence_meter = chappy.create_confidence_meter()
            if confidence_meter:
                st.plotly_chart(confidence_meter, use_container_width=True)
            else:
                st.info("No confidence data yet")

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
            # Update last input time
            st.session_state.last_input_time = datetime.now()
            
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

    # Advanced Visualizations Section
    if chappy.current_state != "sleeping":
        st.header("📊 Brain Visualizations")

        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["🧠 Thought Graph", "📈 Confidence", "🔗 Reasoning Path", "📚 History"])

        with tab1:
            st.subheader("Neuron Activation Network")
            thought_graph = chappy.create_thought_graph()
            if thought_graph:
                st.plotly_chart(thought_graph, use_container_width=True)
            else:
                st.info("No neuron activations to visualize yet. Start a conversation to see the thought graph!")

        with tab2:
            st.subheader("Confidence Over Time")
            confidence_chart = chappy.create_confidence_chart()
            if confidence_chart:
                st.plotly_chart(confidence_chart, use_container_width=True)
            else:
                st.info("No confidence data yet. Chappy needs to process some inputs first!")

        with tab3:
            st.subheader("Current Reasoning Path")
            reasoning_viz = chappy.create_reasoning_path_visualization()
            if reasoning_viz:
                st.markdown(reasoning_viz)
            else:
                st.info("No active reasoning path. Ask Chappy something to see the process!")

            # Interactive neuron details
            st.subheader("🔍 Neuron Inspector")
            if chappy.neuron_pool and chappy.neuron_pool.neurons:
                neuron_names = list(chappy.neuron_pool.neurons.keys())
                selected_neuron = st.selectbox("Select a neuron to inspect:", neuron_names)
                if selected_neuron:
                    details = chappy.get_neuron_details(selected_neuron)
                    if details:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Activations", details['activation_count'])
                            st.metric("Avg Confidence", f"{details['avg_confidence']:.2f}")
                        with col2:
                            st.write(f"**Model:** {details['model']}")
                            st.write(f"**Temperature:** {details['temperature']}")

                        if details['recent_activations']:
                            st.subheader("Recent Activations")
                            for activation in details['recent_activations']:
                                with st.expander(f"Activation at {activation['timestamp'][:19]}"):
                                    st.write(f"**Confidence:** {activation['confidence']:.3f}")
                                    st.write(f"**Content Length:** {activation['content_length']} characters")

                                    # Find related thoughts for this activation
                                    related_thoughts = [t for t in chappy.thought_history[-20:]
                                                      if t['type'] == 'neuron' and selected_neuron in t['content']]
                                    if related_thoughts:
                                        st.write("**Related Thoughts:**")
                                        for thought in related_thoughts[-3:]:  # Last 3 related thoughts
                                            st.write(f"• {thought['content'][:100]}...")

        with tab4:
            st.subheader("Decision History")
            if chappy.decision_history:
                for i, decision in enumerate(chappy.decision_history[-10:]):  # Last 10 decisions
                    with st.expander(f"Decision {len(chappy.decision_history)-i}: {decision['decision']}"):
                        st.write(f"**Time:** {decision['timestamp'][:19]}")
                        st.write(f"**Reasoning:** {decision['reasoning']}")
                        st.write(f"**Threat Level:** {decision['threat_level']:.2f}")
                        st.write(f"**Urgency:** {decision['urgency']:.2f}")
            else:
                st.info("No executive decisions made yet.")

            st.subheader("Export Data")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Export Confidence Data"):
                    if chappy.confidence_history:
                        df = pd.DataFrame(chappy.confidence_history)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="confidence_history.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No confidence data to export")

            with col2:
                if st.button("🧠 Export Neuron Data"):
                    if chappy.neuron_activations:
                        df = pd.DataFrame(chappy.neuron_activations)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="neuron_activations.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No neuron data to export")

            with col3:
                if st.button("📋 Export Thoughts"):
                    if chappy.thought_history:
                        df = pd.DataFrame(chappy.thought_history)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="thought_history.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No thought data to export")

            st.subheader("Memory Palace Summary")
            if chappy.memory_palace:
                memory_summary = chappy.memory_palace.get_chain_summary()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Memories", memory_summary.get('total_memories', 0))
                with col2:
                    st.metric("Active Chains", memory_summary.get('active_chains', 0))
                with col3:
                    st.metric("Avg Relevance", f"{memory_summary.get('avg_relevance', 0):.2f}")

    # Live thought stream
    if chappy.current_state != "sleeping":
        st.header("🔴 Live Thought Stream")
        thoughts_container = st.empty()

        while True:
            # Check for auto-prompt every 2 seconds
            if 'last_input_time' in st.session_state:
                time_since_last_input = (datetime.now() - st.session_state.last_input_time).total_seconds()
                if time_since_last_input > 60:  # 1 minute
                    auto_prompts = [
                        "What should I think about next?",
                        "I'm feeling curious about something new. What comes to mind?",
                        "Time to explore a new idea. What's interesting right now?",
                        "My brain is active. What topic should I dive into?",
                        "I wonder what thoughts are brewing in my neurons..."
                    ]
                    import random
                    auto_prompt = random.choice(auto_prompts)
                    
                    # Add auto-prompt as user message
                    st.session_state.messages.append({"role": "user", "content": f"🤖 *Auto-prompt:* {auto_prompt}"})
                    
                    # Process with Chappy's brain
                    try:
                        response = chappy.process_input(auto_prompt)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.last_input_time = datetime.now()  # Reset timer after auto-processing
                        st.rerun()  # Force UI update
                    except Exception as e:
                        error_msg = f"Oops! Chappy had a brain freeze during auto-thought: {e}"
                        chappy.add_thought("❌", f"Auto-prompt error: {e}", "error")
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

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