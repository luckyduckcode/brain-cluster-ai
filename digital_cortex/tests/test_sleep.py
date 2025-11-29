"""Test the Sleep Cycle."""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.memory_palace import MemoryPalaceChain
from digital_cortex.sleep import Dreamer, Consolidator
from digital_cortex.utils.message import Message

def test_sleep_cycle():
    """Test Dreaming and Consolidation."""
    print("=" * 60)
    print("Testing Sleep Cycle")
    print("=" * 60)
    
    # 1. Setup Memory Chain with some data
    chain = MemoryPalaceChain()
    
    print("[1] Populating Memory Palace...")
    memories = [
        "The sky is blue",
        "Birds fly in the sky",
        "Airplanes also fly",
        "Blue is a cool color",
        "Red is a warm color",
        "Fire is red and hot",
        "The sun is hot and bright"
    ]
    
    for mem in memories:
        chain.store_memory(Message.create("Test", mem, 1.0))
        
    print(f"✓ Stored {len(memories)} memories")
    
    # 2. Test Dreaming
    print("\n[2] Testing Dreamer (Random Walk)...")
    dreamer = Dreamer(chain)
    dream = dreamer.dream(steps=5)
    
    for item in dream:
        type_icon = "💭" if item['type'] == 'hallucination' else "👁️"
        print(f"  {type_icon} {item['content']}")
        
    if len(dream) > 0:
        print("✓ Dreaming successful")
    else:
        print("❌ Dream failed")
        
    # 3. Test Consolidation
    print("\n[3] Testing Consolidator (Pattern Extraction)...")
    consolidator = Consolidator(chain)
    report = consolidator.consolidate()
    
    print(f"  Status: {report['status']}")
    print(f"  Themes found: {report['themes']}")
    print(f"  Meta-memory stored at: {report['meta_memory_address']}")
    
    if report['status'] == 'success':
        print("✓ Consolidation successful")
    else:
        print("❌ Consolidation failed")
        
    print("\n" + "=" * 60)
    print("✓ Sleep Cycle test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_sleep_cycle()
