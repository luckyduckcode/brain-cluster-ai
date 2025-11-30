#!/usr/bin/env python3
"""
Test script for RAG memory functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from digital_cortex.rag_memory import ChappyRAGMemory, WebSearchTool, VideoUnderstandingTool

def test_rag_memory():
    """Test the RAG memory system"""
    print("🧠 Testing RAG Memory System")
    print("=" * 40)

    # Initialize memory system
    memory = ChappyRAGMemory()
    web_search = WebSearchTool()
    video_tool = VideoUnderstandingTool()
    print("✓ RAG Memory initialized")

    # Test storing a conversation
    user_message = "What is the capital of France?"
    chappy_response = "The capital of France is Paris."

    memory.store_conversation(user_message, chappy_response)
    print("✓ Conversation stored")

    # Test retrieving memories
    query = "What is the capital of France?"
    memories = memory.retrieve_relevant_memories(query, n_results=5)
    print(f"✓ Retrieved {len(memories)} memories for query: '{query}'")

    if memories:
        print("  - Memory content:", memories[0]['content'][:100] + "...")
        print("  - Similarity score:", memories[0]['similarity_score'])

    # Test web search
    try:
        search_results = web_search.search("Python programming", max_results=2)
        print(f"✓ Web search returned {len(search_results)} results")
        if search_results:
            print("  - First result:", search_results[0]['title'][:50] + "...")
    except Exception as e:
        print(f"⚠ Web search failed: {e}")

    # Test video understanding
    try:
        video_info = video_tool.get_video_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("✓ Video transcript retrieved")
        if video_info:
            print("  - Video title:", video_info.get('title', 'Unknown'))
    except Exception as e:
        print(f"⚠ Video transcript failed: {e}")

    print("=" * 40)
    print("🎉 RAG Memory tests completed!")

if __name__ == "__main__":
    test_rag_memory()