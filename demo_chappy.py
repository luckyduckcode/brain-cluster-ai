#!/usr/bin/env python3
"""
Chappy GUI Demo - Test the GUI components without running the full server
"""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from chappy_gui import ChappyBrainGUI
import time

def demo_chappy_brain():
    """Demonstrate Chappy's brain components."""
    print("🧠 Chappy the Brain Cluster - Component Demo")
    print("=" * 60)

    # Initialize Chappy
    chappy = ChappyBrainGUI()
    print("✅ Chappy brain initialized")

    # Test brain initialization (without LLM)
    print("\n🔧 Testing brain component initialization...")

    # Mock the components for demo (since we don't have Ollama running)
    try:
        from digital_cortex.corpus_colosseum import CorpusColosseum
        from digital_cortex.memory_palace import MemoryPalaceChain
        from digital_cortex.sensorium import Sensorium
        from digital_cortex.amygdala import Amygdala
        from digital_cortex.frontal_lobe import FrontalLobe
        from digital_cortex.feedback.learner import WeightLearner

        chappy.colosseum = CorpusColosseum()
        chappy.memory_palace = MemoryPalaceChain()
        chappy.sensorium = Sensorium()
        chappy.amygdala = Amygdala()
        chappy.frontal_lobe = FrontalLobe()
        chappy.learner = WeightLearner()
        chappy.current_state = "awake"

        print("✅ All brain components initialized successfully")

        # Test thought system
        print("\n💭 Testing thought system...")
        chappy.add_thought("🌅", "Good morning! Chappy is waking up.", "system")
        chappy.add_thought("🧠", "Initializing neural networks...", "system")
        chappy.add_thought("💡", "Ready to process information!", "system")

        thoughts = chappy.get_recent_thoughts(3)
        for thought in thoughts:
            print(f"  {thought['icon']} {thought['content']}")

        # Test brain status
        print("\n📊 Testing brain status...")
        status = chappy.get_brain_status()
        print(f"  State: {status['state']}")
        print(f"  Neurons: {status['neurons']}")
        print(f"  Memories: {status['memories']['total_memories']}")
        print(f"  Thoughts: {status['thoughts']}")

        print("\n🎨 GUI Components Test Complete!")
        print("To run the full interactive GUI:")
        print("  python launch_chappy.py")
        print("\nMake sure Ollama is running for full functionality!")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Note: Full functionality requires Ollama to be running")

if __name__ == "__main__":
    demo_chappy_brain()