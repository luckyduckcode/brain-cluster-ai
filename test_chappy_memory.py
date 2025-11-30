#!/usr/bin/env python3
"""
Simple command-line test of Chappy's memory system
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from digital_cortex.rag_memory import ChappyRAGMemory

class MockNeuron:
    """Mock neuron for testing"""
    async def process_async(self, prompt):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        # Simple mock response - just echo back with memory context
        if "Alex" in prompt:
            return MockResponse("I remember you told me your name is Alex!")
        elif "blue" in prompt.lower():
            return MockResponse("You mentioned that blue is your favorite color!")
        else:
            return MockResponse("I don't have specific memories about that, but I'm learning!")

class SimpleChappyTest:
    """Simple test of Chappy's memory integration"""

    def __init__(self):
        self.rag_memory = ChappyRAGMemory()
        self.neuron = MockNeuron()

    def _build_context_from_memories(self, memories):
        """Build context string from retrieved memories."""
        if not memories:
            return ""

        context_parts = []
        for memory in memories[:3]:  # Limit to top 3 memories
            content = memory.get('content', '')
            score = memory.get('similarity_score', 0)
            if score > 0.05:  # Include memories with any reasonable relevance
                context_parts.append(f"Previous conversation: {content}")

        return "\n".join(context_parts)

    def _create_enhanced_prompt(self, user_input, context):
        """Create an enhanced prompt with context."""
        if not context:
            return user_input

        enhanced_prompt = f"""Based on our previous conversations:

{context}

Current user message: {user_input}

Please respond naturally, referencing our conversation history when relevant."""
        return enhanced_prompt

    async def process_input(self, user_input):
        """Process user input with memory retrieval."""
        print(f"User: {user_input}")

        # Retrieve relevant memories
        context_memories = self.rag_memory.retrieve_relevant_memories(user_input, n_results=3)
        context = self._build_context_from_memories(context_memories)

        print(f"Retrieved {len(context_memories)} memories, context length: {len(context)}")

        # Create enhanced prompt
        enhanced_prompt = self._create_enhanced_prompt(user_input, context)

        # Get response from neuron
        response = await self.neuron.process_async(enhanced_prompt)
        response_content = response.content

        print(f"Chappy: {response_content}")

        # Store conversation in memory
        self.rag_memory.store_conversation(user_input, response_content)

        return response_content

async def main():
    """Test Chappy's memory system"""
    print("🧠 Testing Chappy Memory System")
    print("=" * 50)

    chappy = SimpleChappyTest()

    # First, establish some memories
    print("📝 Establishing initial memories...")
    await chappy.process_input("My name is Alex")
    await chappy.process_input("I love the color blue")
    print()

    # Now test memory retrieval
    print("🔍 Testing memory retrieval...")
    await chappy.process_input("What's my name?")
    await chappy.process_input("What color do I like?")
    await chappy.process_input("Tell me about pizza")  # Should have no memory

    print()
    print("✅ Memory test completed!")
    print(f"Total conversations stored: {chappy.rag_memory.conversation_collection.count()}")

if __name__ == "__main__":
    asyncio.run(main())