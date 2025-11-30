"""Test the Corpus Colosseum consensus mechanism."""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.message import Message


def test_basic_consensus():
    """Test basic consensus with multiple messages."""
    print("=" * 60)
    print("Testing Corpus Colosseum - Basic Consensus")
    print("=" * 60)
    
    # Create Colosseum
    colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.5)
    
    # Scenario: Snake vs Garden Hose (from white paper example)
    print("\nScenario: Multiple agents analyzing a coiled green object\n")
    
    # Sensorium observes
    msg1 = Message.create(
        source="Sensorium",
        content="Object detected: Slim, coiled, green, unknown size",
        confidence=0.6
    )
    colosseum.add_message(msg1)
    print(f"✓ {msg1}")
    
    # Amygdala flags threat (high confidence)
    msg2 = Message.create(
        source="Amygdala",
        content="High threat potential. Requires immediate evasive action",
        confidence=0.9
    )
    colosseum.add_message(msg2)
    print(f"✓ {msg2}")
    
    # Another amygdala-like response (supporting threat hypothesis)
    msg3 = Message.create(
        source="Amygdala_2",
        content="Danger detected. Recommend retreat",
        confidence=0.85
    )
    colosseum.add_message(msg3)
    print(f"✓ {msg3}")
    
    # Logic agent proposes alternative (lower confidence)
    msg4 = Message.create(
        source="Logic_Agent",
        content="Object classification in progress. Likely garden hose. Requires 3 more tokens for conclusive ID",
        confidence=0.4
    )
    colosseum.add_message(msg4)
    print(f"✓ {msg4}")
    
    # Another logic response
    msg5 = Message.create(
        source="Logic_Agent_2",
        content="Pattern matches garden equipment. Low threat probability",
        confidence=0.45
    )
    colosseum.add_message(msg5)
    print(f"✓ {msg5}")
    
    # Find consensus
    print("\n" + "-" * 60)
    print("Finding Consensus...")
    print("-" * 60)
    
    winner, metadata = colosseum.find_consensus()
    
    print(f"\n🏆 WINNER: {winner.source}")
    print(f"   Content: {winner.content}")
    print(f"   Confidence: {winner.confidence:.2f}")
    print(f"\n📊 Metadata:")
    print(f"   Total messages: {metadata['total_messages']}")
    print(f"   Clusters found: {metadata['cluster_count']}")
    print(f"   Method: {metadata['method']}")
    print(f"   Selection: {metadata['selection']}")
    
    if 'winning_cluster_size' in metadata:
        print(f"   Winning cluster size: {metadata['winning_cluster_size']}")
        print(f"   Winning cluster avg confidence: {metadata['winning_cluster_avg_confidence']:.2f}")
    
    print("\n" + "=" * 60)
    print("✓ Test completed successfully!")
    print("=" * 60)
    
    # Reset for next task
    colosseum.reset()
    print(f"\nColosseum state after reset: {colosseum.get_state()}")


def test_single_message():
    """Test with single message."""
    print("\n\n" + "=" * 60)
    print("Testing Corpus Colosseum - Single Message")
    print("=" * 60)
    
    colosseum = CorpusColosseum()
    
    msg = Message.create(
        source="Test_Agent",
        content="Single message test",
        confidence=0.7
    )
    colosseum.add_message(msg)
    
    winner, metadata = colosseum.find_consensus()
    
    print(f"\n🏆 WINNER: {winner.source}")
    print(f"   Method: {metadata['method']}")
    print("\n✓ Single message test passed!")
    print("=" * 60)


def test_attention_consensus():
    """Test attention-based consensus mechanism."""
    print("\n\n" + "=" * 60)
    print("Testing Corpus Colosseum - Attention-Based Consensus")
    print("=" * 60)
    
    colosseum = CorpusColosseum()
    
    # Add messages from different neurons
    msg1 = Message.create("neuron1", "Answer A", 0.8)
    msg2 = Message.create("neuron2", "Answer A", 0.7)  # Same answer, lower confidence
    msg3 = Message.create("neuron3", "Answer B", 0.9)  # Different answer, higher confidence
    
    colosseum.add_message(msg1)
    colosseum.add_message(msg2)
    colosseum.add_message(msg3)
    
    print(f"✓ Added 3 messages from neurons with different answers")
    
    # Test attention consensus
    winner, metadata = colosseum.find_consensus(method="attention")
    
    print(f"\n🏆 WINNER: {winner.source}")
    print(f"   Content: {winner.content}")
    print(f"   Confidence: {winner.confidence:.2f}")
    print(f"\n📊 Metadata:")
    print(f"   Method: {metadata['method']}")
    print(f"   Total messages: {metadata['total_messages']}")
    print(f"   Winning group size: {metadata['winning_group_size']}")
    
    # Should favor the group with higher combined attention weight
    # neuron1 + neuron2 both say "Answer A"
    assert winner.content == "Answer A", f"Expected 'Answer A', got '{winner.content}'"
    
    print("\n✓ Attention consensus test passed!")
    print("=" * 60)


def test_attention_learning():
    """Test that attention weights update over time."""
    print("\n\n" + "=" * 60)
    print("Testing Attention Learning")
    print("=" * 60)
    
    colosseum = CorpusColosseum()
    
    # Check initial weights
    initial_weights = colosseum.get_attention_weights()
    print(f"Initial attention weights: {initial_weights}")
    
    # Simulate positive performance for neuron1
    colosseum.update_neuron_performance("neuron1", 0.5)
    colosseum.update_neuron_performance("neuron1", 0.5)
    
    # Check updated weights
    updated_weights = colosseum.get_attention_weights()
    print(f"Updated attention weights: {updated_weights}")
    
    # neuron1 should have higher weight now
    assert updated_weights["neuron1"] > initial_weights.get("neuron1", 1.0), "Weight should have increased"
    
    print("\n✓ Attention learning test passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_consensus()
    test_single_message()
    test_attention_consensus()
    test_attention_learning()
