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
    
    # Process with all neurons
    print("\n[4] Processing with LLM-neurons...")
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
    print("[5] CORPUS COLOSSEUM - Finding Consensus...")
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
    
    print("\n" + "=" * 70)
    print("✓ Demo completed!")
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
