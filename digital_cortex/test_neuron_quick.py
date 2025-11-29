"""Quick test of LLM-Neuron connectivity."""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.utils.llm_neuron import LLMNeuron

print("Testing LLM-Neuron connection to Ollama...")
print("=" * 60)

# Create a single neuron
neuron = LLMNeuron(
    name="Test_Neuron",
    model="llama3.2:1b",
    system_prompt="You are a helpful assistant. Be brief.",
    temperature=0.5
)

# Simple test
prompt = "What is 2+2? Answer in one sentence."

print(f"\nPrompt: {prompt}")
print("\nProcessing...")

message = neuron.process(prompt, extract_confidence=False)

print(f"\n✓ Response from {message.source}:")
print(f"  {message.content}")
print(f"  Confidence: {message.confidence}")
print(f"  Model: {message.metadata.get('model')}")

print("\n" + "=" * 60)
print("✓ LLM-Neuron test passed!")
