#!/usr/bin/env python3
"""
Test script to populate Chappy's memory with realistic conversations
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chappy_standalone_simple import ChappyBrain

async def populate_memory():
    """Populate memory with test conversations"""
    print("🧠 Populating Chappy's memory with test conversations...")

    # Initialize brain
    brain = ChappyBrain()
    await brain.initialize_async()

    # Test conversations
    conversations = [
        ("Hello Chappy, my name is Alex", "Hello Alex! Nice to meet you. How can I help you today?"),
        ("What's my name?", "Your name is Alex! We just introduced ourselves."),
        ("I like the color blue", "That's a great color choice! Blue is very calming."),
        ("What's my favorite color?", "You mentioned that you like the color blue!"),
        ("Tell me about Python programming", "Python is a popular programming language known for its simplicity and readability."),
        ("What did I ask about earlier?", "You asked about Python programming, and I told you it's a popular language known for its simplicity."),
        ("My favorite food is pizza", "Pizza sounds delicious! What toppings do you like?"),
        ("What food do I like?", "You mentioned that pizza is your favorite food!"),
    ]

    for user_msg, bot_response in conversations:
        print(f"Storing: {user_msg[:30]}...")
        # Simulate the storage that happens in process_input_async
        if brain.rag_memory:
            brain.rag_memory.store_conversation(user_msg, bot_response)
        await asyncio.sleep(0.1)  # Small delay

    print("✅ Memory populated with test conversations")

    # Test retrieval
    print("\n🔍 Testing memory retrieval...")
    test_queries = [
        "What's my name?",
        "What color do I like?",
        "What did I ask about programming?",
        "What's my favorite food?",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        if brain.rag_memory:
            memories = brain.rag_memory.retrieve_relevant_memories(query, n_results=2)
            context = brain._build_context_from_memories(memories)
            print(f"Found {len(memories)} memories")
            if context:
                print(f"Context: {context[:100]}...")
            else:
                print("No relevant context found")

if __name__ == "__main__":
    asyncio.run(populate_memory())