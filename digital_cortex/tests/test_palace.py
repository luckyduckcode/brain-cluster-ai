"""Test the Memory Palace Chain."""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.memory_palace import MemoryPalaceChain
from digital_cortex.utils.message import Message

def test_palace_chain():
    """Test basic functionality of the Memory Palace Chain."""
    print("=" * 60)
    print("Testing Memory Palace Chain")
    print("=" * 60)
    
    # Initialize chain
    chain = MemoryPalaceChain(room_capacity=5)  # Small capacity to test chaining
    print("✓ Initialized Memory Palace Chain")
    
    # Store some memories
    print("\n[1] Storing memories...")
    
    messages = [
        Message.create("Sensorium", "Saw a red apple", 0.9),
        Message.create("Logic", "Apples are fruits", 0.8),
        Message.create("Amygdala", "Hungry for apple", 0.7),
        Message.create("Sensorium", "Apple is shiny", 0.85),
        Message.create("Logic", "Red color indicates ripeness", 0.75),
        Message.create("Executive", "Decision: Eat apple", 0.95)  # Should trigger new room
    ]
    
    for i, msg in enumerate(messages):
        addr = chain.store_memory(msg)
        print(f"  Stored msg #{i+1} at {addr}")
        
    # Verify chaining
    summary = chain.get_chain_summary()
    print(f"\n[2] Chain Summary:")
    print(f"  Total Rooms: {summary['total_rooms']}")
    print(f"  Total Memories: {summary['total_memories']}")
    print(f"  Current Room: {summary['current_room_id']}")
    
    if summary['total_rooms'] >= 2:
        print("✓ Successfully created new room when capacity reached")
    else:
        print("❌ Failed to create new room")
        
    # Test retrieval
    print("\n[3] Testing Retrieval...")
    recent = chain.get_recent_memories(3)
    print(f"  Retrieved {len(recent)} recent memories")
    for mem in recent:
        print(f"  - {mem['content']} (Room {mem['room_id']})")
        
    # Test traversal (Internal Voice)
    print("\n[4] Testing Chain Traversal (Internal Voice)...")
    traversal = chain.traverse_forward()
    print(f"  Traversed {len(traversal)} rooms")
    
    print("\n" + "=" * 60)
    print("✓ Memory Palace Chain test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_palace_chain()
