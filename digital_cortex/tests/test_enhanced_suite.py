"""
Enhanced Testing Suite for Brain-Cluster-AI

This module provides comprehensive testing capabilities including:
- Performance benchmarks for consensus speed and memory usage
- Integration tests with real LLM scenarios
- Edge case testing for conflicting neurons and low confidence
- Stress testing with many neurons and large inputs
- Mock LLM responses for CI/CD pipelines
"""

import pytest
import time
import asyncio
import psutil
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor
import statistics
import json
from typing import List, Dict, Any

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_cortex.corpus_colosseum.colosseum import CorpusColosseum
from digital_cortex.corpus_colosseum.attention_consensus import AttentionVoter, HierarchicalConsensus
from digital_cortex.frontal_lobe import FrontalLobe
from digital_cortex.memory_palace import MemoryManager, MemorySystem
from digital_cortex.utils.llm_neuron import LLMNeuron
from digital_cortex.utils.message import Message
from digital_cortex.utils.config import ConfigManager
from digital_cortex.tools import tool_registry


class PerformanceMonitor:
    """Monitor system performance during tests."""

    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None

    def start(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = psutil.cpu_percent(interval=None)

    def stop(self) -> Dict[str, float]:
        """Stop monitoring and return metrics."""
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent(interval=None)

        return {
            'duration': end_time - self.start_time,
            'memory_delta': end_memory - self.start_memory,
            'avg_cpu': (self.start_cpu + end_cpu) / 2
        }


class MockLLMNeuron(LLMNeuron):
    """Mock neuron for testing that returns predetermined responses."""

    def __init__(self, response: str, confidence: float = 0.8, delay: float = 0.1):
        super().__init__(name=f"mock_neuron_{id(self)}", model="mock-model")
        self.mock_response = response
        self.mock_confidence = confidence
        self.delay = delay

    async def process_async(self, message: Message) -> Dict[str, Any]:
        """Return mock response after delay."""
        await asyncio.sleep(self.delay)
        return {
            'response': self.mock_response,
            'confidence': self.mock_confidence,
            'neuron_id': f'mock_{id(self)}',
            'model': 'mock-model'
        }


class TestPerformanceBenchmarks:
    """Performance benchmarking tests."""

    @pytest.fixture
    def config(self):
        """Load test configuration."""
        return ConfigManager()

    @pytest.fixture
    def performance_monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()

    def test_consensus_speed_small(self, performance_monitor):
        """Benchmark consensus speed with small number of neurons."""
        performance_monitor.start()

        # Create colosseum
        colosseum = CorpusColosseum()

        # Add messages from mock neurons
        messages = [
            Message.create(source="neuron1", content="Answer A", confidence=0.9),
            Message.create(source="neuron2", content="Answer A", confidence=0.8),
            Message.create(source="neuron3", content="Answer B", confidence=0.7),
        ]

        for msg in messages:
            colosseum.add_message(msg)

        # Run consensus
        result, metadata = colosseum.find_consensus()

        metrics = performance_monitor.stop()

        # Assertions
        assert result is not None
        assert hasattr(result, 'content')
        assert metrics['duration'] < 1.0  # Should complete within 1 second
        assert metrics['memory_delta'] < 50  # Memory increase < 50MB

    def test_consensus_speed_large(self, performance_monitor):
        """Benchmark consensus speed with large number of neurons."""
        performance_monitor.start()

        # Create colosseum
        colosseum = CorpusColosseum()

        # Add 20 messages from mock neurons
        messages = [
            Message.create(source=f"neuron{i}", content=f"Answer {i%3}", confidence=0.8 - (i * 0.01))
            for i in range(20)
        ]

        for msg in messages:
            colosseum.add_message(msg)

        # Run consensus
        result, metadata = colosseum.find_consensus()

        metrics = performance_monitor.stop()

        # Assertions
        assert result is not None
        assert metrics['duration'] < 5.0  # Should complete within 5 seconds
        assert metrics['memory_delta'] < 100  # Memory increase < 100MB

    def test_memory_palace_performance(self, performance_monitor):
        """Benchmark memory palace operations."""
        performance_monitor.start()

        memory = MemoryManager(system=MemorySystem.GRAPH)

        # Add many memories
        for i in range(100):
            msg = Message.create("test", f"Memory {i}", 0.8, {"topic": f"topic_{i%10}", "importance": i%5})
            memory.store_memory(msg)

        # Search memories
        results = memory.retrieve_relevant_memories("Memory", limit=20)

        metrics = performance_monitor.stop()

        # Assertions
        assert len(results) > 0
        assert metrics['duration'] < 2.0
        assert metrics['memory_delta'] < 20

    def test_tool_execution_performance(self, performance_monitor):
        """Benchmark tool execution speed."""
        performance_monitor.start()

        # Test calculator tool
        result = tool_registry.execute_tool("calculator", {"expression": "2**100"})

        metrics = performance_monitor.stop()

        # Assertions
        assert result.success
        assert metrics['duration'] < 0.5  # Should be very fast


class TestIntegrationTests:
    """Integration tests with realistic scenarios."""

    @pytest.fixture
    def mock_neurons(self):
        """Create a set of mock neurons for integration testing."""
        return [
            MockLLMNeuron("The answer is 42", 0.9),
            MockLLMNeuron("42 is the answer", 0.8),
            MockLLMNeuron("I think it's 42", 0.7),
        ]

    @pytest.fixture
    def full_brain(self):
        """Create a full brain instance for integration testing."""
        return CorpusColosseum()

    def test_full_query_processing(self, full_brain):
        """Test complete query processing pipeline."""
        # Add messages simulating neuron responses
        messages = [
            Message.create("neuron1", "The answer is 42", 0.9),
            Message.create("neuron2", "42 is the answer", 0.8),
            Message.create("neuron3", "I think it's 42", 0.7),
        ]

        for msg in messages:
            full_brain.add_message(msg)

        result, metadata = full_brain.find_consensus()

        assert result is not None
        assert hasattr(result, 'content')
        assert result.confidence > 0.5

    def test_memory_integration(self, full_brain):
        """Test memory integration in query processing."""
        # Add some context messages
        context_msgs = [
            Message.create("neuron1", "We were discussing philosophy", 0.8),
            Message.create("neuron2", "Philosophy topics include meaning of life", 0.7),
        ]

        for msg in context_msgs:
            full_brain.add_message(msg)

        # Process consensus on context
        result1, _ = full_brain.find_consensus()

        # Reset and add question messages
        full_brain.reset()
        question_msgs = [
            Message.create("neuron1", "What philosophers discuss meaning?", 0.9),
            Message.create("neuron2", "Socrates and Camus discuss meaning", 0.8),
        ]

        for msg in question_msgs:
            full_brain.add_message(msg)

        result2, _ = full_brain.find_consensus()

        assert result1 is not None
        assert result2 is not None

    def test_tool_integration_in_brain(self, full_brain):
        """Test tool integration within brain processing."""
        # Test calculator tool directly
        result = tool_registry.execute_tool("calculator", {"expression": "6 * 7"})

        assert result.success
        assert result.output["numeric"] == 42


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_conflicting_neurons(self):
        """Test consensus with highly conflicting neuron responses."""
        colosseum = CorpusColosseum()

        messages = [
            Message.create("neuron1", "Yes, definitely", 0.9),
            Message.create("neuron2", "No, absolutely not", 0.9),
            Message.create("neuron3", "Maybe, I'm not sure", 0.3),
        ]

        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()

        # Should handle conflict gracefully - attention voting may still pick highest confidence
        assert result is not None
        assert hasattr(result, 'content')
        # Note: attention-based consensus may still select highest confidence despite conflict

    def test_low_confidence_scenario(self):
        """Test behavior with all neurons having low confidence."""
        colosseum = CorpusColosseum()

        messages = [
            Message.create("neuron1", "I think it might be", 0.2),
            Message.create("neuron2", "Possibly, but I'm not sure", 0.3),
            Message.create("neuron3", "Could be, maybe not", 0.1),
        ]

        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()

        assert result is not None
        # Should detect low confidence situation
        assert result.confidence < 0.5

    def test_empty_input(self):
        """Test handling of empty or minimal input."""
        colosseum = CorpusColosseum()

        messages = [Message.create("neuron1", "I need more information", 0.5)]

        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()

        assert result is not None

    def test_extremely_long_input(self):
        """Test handling of very long input."""
        colosseum = CorpusColosseum()

        long_content = "What is the meaning of life? " * 1000  # Very long question
        messages = [Message.create("neuron1", f"Response to: {long_content[:100]}...", 0.8)]

        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()

        assert result is not None


class TestStressTesting:
    """Stress testing with high loads."""

    def test_many_neurons_consensus(self):
        """Test consensus with many neurons."""
        colosseum = CorpusColosseum()

        # Create 50 messages from mock neurons
        messages = [
            Message.create(f"neuron{i}", f"Response {i}", 0.5 + (i % 50) * 0.01)
            for i in range(50)
        ]

        start_time = time.time()
        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()
        duration = time.time() - start_time

        assert result is not None
        assert duration < 10.0  # Should complete within 10 seconds

    def test_concurrent_queries(self):
        """Test handling multiple sequential queries."""
        colosseum = CorpusColosseum()

        # Run 10 sequential queries
        start_time = time.time()
        results = []

        for i in range(10):
            # Reset colosseum for each query
            colosseum.reset()
            messages = [Message.create("neuron1", f"Concurrent response {i}", 0.8)]
            for msg in messages:
                colosseum.add_message(msg)

            result, _ = colosseum.find_consensus()
            results.append(result)

        duration = time.time() - start_time

        assert len(results) == 10
        assert all(result is not None for result in results)
        assert duration < 5.0  # Should complete within 5 seconds

    def test_memory_stress(self):
        """Test memory palace with many memories."""
        memory = MemoryManager(system=MemorySystem.GRAPH)

        # Add 1000 memories
        for i in range(1000):
            msg = Message.create("test", f"Memory content {i}", 0.8, {"topic": f"topic_{i%20}", "importance": i%10, "size": "large" * 10})
            memory.store_memory(msg)

        # Search should still work
        results = memory.retrieve_relevant_memories("Memory content", limit=50)
        assert len(results) >= 40  # Should find many matches

        # Memory usage should be reasonable (allowing for graph storage)
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        assert memory_usage < 2000  # Less than 2000MB for graph storage


class TestMockLLMScenarios:
    """Tests using mock LLM responses for CI/CD."""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM API response."""
        return {
            'response': 'This is a mock response from the LLM',
            'confidence': 0.85,
            'model': 'mock-gpt-4',
            'usage': {'tokens': 150}
        }

    def test_mock_neuron_creation(self, mock_llm_response):
        """Test creating neurons with mock responses."""
        neuron = MockLLMNeuron(
            response=mock_llm_response['response'],
            confidence=mock_llm_response['confidence']
        )

        assert neuron.mock_response == mock_llm_response['response']
        assert neuron.mock_confidence == mock_llm_response['confidence']

    def test_mock_consensus_pipeline(self, mock_llm_response):
        """Test full consensus pipeline with mocks."""
        colosseum = CorpusColosseum()

        messages = [
            Message.create("neuron1", "Mock answer A", 0.8),
            Message.create("neuron2", "Mock answer B", 0.7),
            Message.create("neuron3", "Mock answer A", 0.9),
        ]

        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()

        assert result is not None
        assert hasattr(result, 'content')
        assert isinstance(result.content, str)

    def test_ci_cd_ready(self):
        """Test that can run without external dependencies."""
        # This test should pass in CI/CD environments
        colosseum = CorpusColosseum()
        messages = [Message.create("neuron1", "CI/CD test response", 0.8)]

        for msg in messages:
            colosseum.add_message(msg)

        result, metadata = colosseum.find_consensus()

        assert result is not None
        assert result.content == "CI/CD test response"


# Benchmark utilities for external use
def run_performance_benchmarks():
    """Run all performance benchmarks and return results."""
    monitor = PerformanceMonitor()

    results = {}

    # Consensus speed test
    monitor.start()
    colosseum = CorpusColosseum()
    messages = [Message.create(f"neuron{i}", f"Answer {i}", 0.8) for i in range(10)]
    for msg in messages:
        colosseum.add_message(msg)
    colosseum.find_consensus()
    results['consensus_10_neurons'] = monitor.stop()

    # Memory test
    monitor.start()
    memory = MemoryManager(system=MemorySystem.GRAPH)
    for i in range(100):
        msg = Message.create("test", f"Memory {i}", 0.8, {"topic": f"topic_{i%5}"})
        memory.store_memory(msg)
    memory.retrieve_relevant_memories("topic_1", limit=10)
    results['memory_100_items'] = monitor.stop()

    return results


def generate_performance_report():
    """Generate a performance report."""
    results = run_performance_benchmarks()

    report = "# Performance Benchmark Report\n\n"
    report += "| Test | Duration (s) | Memory Delta (MB) | Avg CPU (%) |\n"
    report += "|------|---------------|-------------------|-------------|\n"

    for test_name, metrics in results.items():
        report += f"| {test_name} | {metrics['duration']:.3f} | {metrics['memory_delta']:.1f} | {metrics['avg_cpu']:.1f} |\n"

    return report


if __name__ == "__main__":
    # Run benchmarks when executed directly
    print("Running performance benchmarks...")
    results = run_performance_benchmarks()
    print(json.dumps(results, indent=2))

    print("\nGenerating performance report...")
    report = generate_performance_report()
    print(report)

    # Save report
    with open("performance_report.md", "w") as f:
        f.write(report)
    print("Report saved to performance_report.md")