#!/usr/bin/env python3
"""
Demo: Chappy's YouTube Learning System

This script demonstrates Chappy's ability to learn from YouTube videos
through multimodal processing and knowledge extraction.
"""

import asyncio
import sys
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

from digital_cortex.learning_center import VideoLearningContainer
from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.memory_palace import MemoryManager, MemorySystem
from digital_cortex.utils.message import Message


async def demo_video_learning():
    """Demonstrate the video learning system"""
    print("🎥 Chappy's YouTube Learning System Demo")
    print("=" * 50)

    # Initialize brain components
    print("🧠 Initializing brain components...")
    colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.4)
    memory_palace = MemoryManager(system=MemorySystem.GRAPH, max_nodes=5000)

    # Initialize video learning container
    print("🎬 Initializing video learning container...")
    video_container = VideoLearningContainer(colosseum, memory_palace)

    success = await video_container.initialize()
    if not success:
        print("❌ Failed to initialize video learning container")
        return

    print("✅ Video learning system ready!")
    print()

    # Demo commands
    demo_commands = [
        "learning stats",
        "what do you know about machine learning?",
        "find videos about neural networks"
    ]

    print("📝 Testing knowledge retrieval (before learning)...")
    for command in demo_commands:
        print(f"\n💬 User: {command}")
        message = Message.create(source="demo_user", content=command, confidence=1.0)
        response = await video_container.process_message(message)
        if response:
            print(f"🎯 Chappy: {response.content}")
        else:
            print("🤔 Chappy: I don't understand that command.")

    print("\n" + "=" * 50)
    print("🎬 To learn from a YouTube video, use:")
    print("💬 'learn from video: https://youtube.com/watch?v=VIDEO_ID'")
    print("\n📚 Example video learning commands:")
    print("• learn from video: https://youtube.com/watch?v=dQw4w9WgXcQ")
    print("• what do you know about artificial intelligence?")
    print("• find videos about machine learning")
    print("• learning stats")

    # Cleanup
    await video_container.shutdown()
    print("\n🧹 Demo completed and cleaned up!")


if __name__ == "__main__":
    asyncio.run(demo_video_learning())