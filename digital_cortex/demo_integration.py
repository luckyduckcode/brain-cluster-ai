"""
Digital Cortex Integration Demo

This demonstrates the complete feedback cycle:
1. Multiple LLM-neurons process a scenario
2. Corpus Colosseum finds consensus
3. System makes a decision
"""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.llm_neuron import LLMNeuron, NeuronPool
from digital_cortex.utils.message import Message
from digital_cortex.feedback.learner import WeightLearner
from digital_cortex.memory_palace import MemoryPalaceChain
from digital_cortex.sensorium import Sensorium
from digital_cortex.amygdala import Amygdala
from digital_cortex.frontal_lobe import FrontalLobe


def demo_snake_scenario():
    """
    Recreate the snake vs garden hose scenario from the white paper,
    but with REAL LLMs making the decisions.
    """
    print("=" * 70)
    print("DIGITAL CORTEX INTEGRATION DEMO")
    print("Scenario: Coiled Green Object Detection")
    print("=" * 70)
    
    # Initialize Corpus Colosseum
    print("\n[1] Initializing Corpus Colosseum...")
    colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.4)
    
    # Create neuron pool
    print("[2] Creating LLM-Neuron pool...")
    pool = NeuronPool()
    
    # Create specialized neurons with different roles
    print("\n[3] Spawning specialized neurons...")
    
    # Amygdala-type neurons (threat assessment)
    pool.create_neuron(
        name="Amygdala_Threat",
        model="llama3.2:1b",
        system_prompt="You are a threat assessment system. Evaluate danger quickly and decisively. Be cautious and prioritize safety.",
        temperature=0.3  # Low temperature for consistent threat assessment
    )
    
    pool.create_neuron(
        name="Amygdala_Risk",
        model="llama3.2:1b",
        system_prompt="You assess risk and urgency. When uncertain, err on the side of caution.",
        temperature=0.4
    )
    
    # Logic-type neurons (analytical reasoning)
    pool.create_neuron(
        name="Logic_Analyzer",
        model="llama3.2:1b",
        system_prompt="You are a logical analysis system. Carefully examine evidence and avoid jumping to conclusions. Consider multiple hypotheses.",
        temperature=0.6
    )
    
    pool.create_neuron(
        name="Logic_Classifier",
        model="llama3.2:1b",
        system_prompt="You classify objects based on visual features. Be methodical and request more data when needed.",
        temperature=0.5
    )
    
    print(f"✓ Created {len(pool.list_neurons())} neurons: {pool.list_neurons()}")
    
    # The scenario
    observation = """
    OBSERVATION: You detect a coiled, green object in the grass ahead.
    
    VISUAL FEATURES:
    - Shape: Coiled/curved
    - Color: Green
    - Texture: Smooth, possibly scaled
    - Size: Approximately 1-2 meters long
    - Context: Outdoor garden area
    - Movement: None detected yet
    
    TASK: Analyze this object and recommend an action. What is it, and what should we do?
    """
    
    print("\n" + "=" * 70)
    print("OBSERVATION:")
    print(observation)
    print("=" * 70)
    
    # 4. SENSORIUM - Process the observation
    print("\n[4] SENSORIUM - Processing sensory input...")
    print("=" * 70)
    
    sensorium = Sensorium()
    
    # Process the text observation
    sensory_message = sensorium.process_text(
        observation.strip(),
        source="scenario_input",
        metadata={"scenario": "snake_vs_hose", "input_type": "visual_observation"}
    )
    
    print(f"✓ Sensorium processed input: {sensory_message.content[:100]}...")
    print(f"  Confidence: {sensory_message.confidence:.2f}")
    print(f"  Analysis: {sensory_message.metadata['text_analysis']['word_count']} words")
    
    # Add sensory message to Colosseum for context
    colosseum.add_message(sensory_message)
    print("✓ Sensory input added to Corpus Colosseum")
    
    # 5. AMYGDALA - Threat and urgency assessment
    print("\n[5] AMYGDALA - Threat and Urgency Assessment")
    print("=" * 70)
    
    amygdala = Amygdala()
    
    # Process the sensory message through Amygdala
    amygdala_message = amygdala.process_message(sensory_message)
    
    print(f"✓ Amygdala processed: {amygdala_message.content[:80]}...")
    print(f"  Source: {amygdala_message.source}")
    print(f"  Confidence: {sensory_message.confidence:.2f} -> {amygdala_message.confidence:.2f}")
    
    # Extract assessment details
    assessment = amygdala_message.metadata["amygdala_assessment"]
    print(f"  Threat Level: {assessment['threat_level']:.2f}")
    print(f"  Urgency: {assessment['urgency']:.2f}")
    print(f"  Valence: {assessment['valence']:.2f}")
    print(f"  Triggers: {assessment['triggers'][:3]}...")  # Show first 3
    
    # Add Amygdala-enhanced message to Colosseum
    colosseum.add_message(amygdala_message)
    print("✓ Amygdala assessment added to Corpus Colosseum")
    
    # Process with all neurons
    print("\n[6] Processing with LLM-neurons...")
    print("-" * 70)
    
    messages = pool.process_parallel(observation)
    
    # Display each neuron's response
    for msg in messages:
        print(f"\n🧠 {msg.source} (confidence: {msg.confidence:.2f})")
        print(f"   Model: {msg.metadata.get('model', 'unknown')}")
        print(f"   Response: {msg.content[:200]}...")
        
        # Add to Colosseum
        colosseum.add_message(msg)
    
    # Find consensus
    print("\n" + "=" * 70)
    print("[7] CORPUS COLOSSEUM - Finding Consensus...")
    print("=" * 70)
    
    winner, metadata = colosseum.find_consensus()
    
    if winner:
        print(f"\n🏆 CONSENSUS REACHED")
        print(f"   Winning Neuron: {winner.source}")
        print(f"   Confidence: {winner.confidence:.2f}")
        print(f"   Decision: {winner.content}")
        print(f"\n📊 Consensus Metadata:")
        print(f"   Total neurons: {metadata['total_messages']}")
        print(f"   Clusters found: {metadata['cluster_count']}")
        print(f"   Selection method: {metadata['selection']}")
        
        if 'winning_cluster_size' in metadata:
            print(f"   Cluster size: {metadata['winning_cluster_size']}")
            print(f"   Cluster avg confidence: {metadata['winning_cluster_avg_confidence']:.2f}")
        
        # 8. FEEDBACK LEARNING - Temporal Credit Assignment
        print(f"\n[8] FEEDBACK LEARNING - Temporal Credit Assignment")
        print("=" * 70)
        
        learner = WeightLearner(storage_path="demo_weights.json")
        
        # Get contributing neurons from consensus metadata
        contributing_neurons = metadata.get('contributing_neurons', [winner.source])
        print(f"Contributing neurons: {contributing_neurons}")
        
        # Simulate outcome assessment (in a real system, this would come from Motor Cortex)
        # For demo purposes, assume the decision was correct (positive score)
        outcome_score = 0.8  # Positive reinforcement
        
        print(f"Simulated outcome assessment: Score = {outcome_score}")
        print("Applying temporal credit assignment...")
        
        # Show weights before learning
        print("Weights before learning:")
        for neuron in contributing_neurons:
            weight = learner.get_weight(neuron)
            print(f"  {neuron}: {weight:.2f}")
        
        # Apply temporal credit assignment
        learner.update_contributing_neurons(contributing_neurons, outcome_score)
        
        # Show weights after learning
        print("Weights after learning:")
        for neuron in contributing_neurons:
            weight = learner.get_weight(neuron)
            print(f"  {neuron}: {weight:.2f}")
        
        print("✓ Learning completed!")
        
        # 9. MEMORY PALACE - Store Decision for Long-term Memory
        print(f"\n[9] MEMORY PALACE - Long-term Episodic Storage")
        print("=" * 70)
        
        memory_chain = MemoryPalaceChain(room_capacity=10)  # Small capacity for demo
        
        # Prepare outcome data from the feedback learning
        outcome_data = {
            "outcome_score": outcome_score,
            "contributing_neurons": contributing_neurons,
            "consensus_metadata": metadata,
            "learning_applied": True
        }
        
        # Store the consensus decision in long-term memory
        memory_address = memory_chain.store_memory(winner, outcome_data)
        print(f"Stored consensus decision in Memory Palace at: {memory_address}")
        
        # Show current memory chain status
        summary = memory_chain.get_chain_summary()
        print(f"Memory Chain Status:")
        print(f"  Total Rooms: {summary['total_rooms']}")
        print(f"  Total Memories: {summary['total_memories']}")
        print(f"  Current Room: {summary['current_room_id']}")
        
        # Demonstrate retrieval
        retrieved = memory_chain.retrieve_memory(memory_address)
        if retrieved:
            print(f"✓ Successfully retrieved memory: {retrieved['content'][:50]}...")
        else:
            print("❌ Failed to retrieve memory")
        
        print("✓ Memory storage completed!")
        
        # 10. FRONTAL LOBE - Executive Decision Making
        print(f"\n[10] FRONTAL LOBE - Executive Decision Making")
        print("=" * 70)
        
        frontal_lobe = FrontalLobe()
        
        # Prepare context for executive decision
        amygdala_assessment = amygdala_message.metadata.get("amygdala_assessment", {})
        sensory_context = sensory_message.metadata
        memory_context = {
            "count": summary['total_memories'],
            "recent_decisions": [winner.content],
            "patterns": "threat_assessment"
        }
        
        # Available actions for this scenario
        available_actions = [
            "investigate_further",
            "proceed_normally", 
            "alert_user",
            "retreat_safely",
            "document_findings"
        ]
        
        print("Making executive decision with full context...")
        print(f"  Amygdala threat level: {amygdala_assessment.get('threat_level', 0):.2f}")
        print(f"  Sensory input: {sensory_context.get('sensorium_type', 'unknown')}")
        print(f"  Memory patterns: {memory_context['patterns']}")
        print(f"  Available actions: {available_actions}")
        
        # Make executive decision
        executive_decision = frontal_lobe.make_executive_decision(
            winner,  # consensus message
            amygdala_assessment,
            sensory_context,
            [memory_context],  # memory context as list
            available_actions
        )
        
        print(f"\n🎯 EXECUTIVE DECISION")
        print(f"   Decision: {executive_decision.decision}")
        print(f"   Confidence: {executive_decision.confidence:.2f}")
        print(f"   Reasoning: {executive_decision.reasoning[:100]}...")
        print(f"   Risk Assessment: {executive_decision.risk_assessment}")
        print(f"   Action Plan ({len(executive_decision.action_plan)} steps):")
        for i, action in enumerate(executive_decision.action_plan, 1):
            print(f"     {i}. {action}")
        print(f"   Alternatives Considered: {executive_decision.alternatives_considered}")
        print(f"   Meta-cognition: {executive_decision.meta_cognition[:80]}...")
        
        print("✓ Executive decision making completed!")
    
    print("\n" + "=" * 70)
    print("✓ Complete Digital Cortex Demo completed!")
    print("=" * 70)
    
    return winner, metadata


def demo_simple_question():
    """Simple demo with a straightforward question."""
    print("\n\n" + "=" * 70)
    print("SIMPLE QUESTION DEMO")
    print("=" * 70)
    
    colosseum = CorpusColosseum()
    pool = NeuronPool()
    
    # Create diverse neurons
    pool.create_neuron("Optimist", model="llama3.2:1b", 
                      system_prompt="You are optimistic and see the bright side.",
                      temperature=0.8)
    
    pool.create_neuron("Realist", model="llama3.2:1b",
                      system_prompt="You are pragmatic and realistic.",
                      temperature=0.5)
    
    pool.create_neuron("Analyst", model="llama3.2:1b",
                      system_prompt="You analyze data carefully.",
                      temperature=0.3)
    
    question = "Should we invest time in building AGI systems? Give a brief answer."
    
    print(f"\nQuestion: {question}\n")
    
    messages = pool.process_parallel(question)
    
    for msg in messages:
        print(f"🧠 {msg.source}: {msg.content[:150]}... (confidence: {msg.confidence:.2f})")
        colosseum.add_message(msg)
    
    winner, _ = colosseum.find_consensus()
    
    if winner:
        print(f"\n🏆 Consensus: {winner.source}")
        print(f"   {winner.content}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n🧠 DIGITAL CORTEX - Live Demo with Real LLMs\n")
    print("NOTE: This requires Ollama to be running with llama3.2:1b model")
    print("      Start Ollama: 'ollama serve' in another terminal\n")
    
    try:
        # Run the main demo
        demo_snake_scenario()
        
        # Uncomment to run simple demo too
        # demo_simple_question()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Ollama is running: 'ollama serve'")
        print("And that you have the model: 'ollama pull llama3.2:1b'")
