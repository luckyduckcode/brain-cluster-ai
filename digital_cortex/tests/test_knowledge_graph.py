#!/usr/bin/env python3
"""
Test Knowledge Graph Memory System

Tests for the graph-based memory system.
"""

import unittest
from unittest.mock import MagicMock
from digital_cortex.memory_palace.knowledge_graph import KnowledgeGraphMemory, MemoryNode
from digital_cortex.memory_palace.memory_manager import MemoryManager, MemorySystem
from digital_cortex.utils.message import Message

class TestMemoryNode(unittest.TestCase):
    def setUp(self):
        self.node = MemoryNode("test_1", "Test content", {"source": "test"})

    def test_node_creation(self):
        self.assertEqual(self.node.node_id, "test_1")
        self.assertEqual(self.node.content, "Test content")
        self.assertEqual(self.node.metadata["source"], "test")

    def test_add_connection(self):
        self.node.add_connection("node_2", "semantic", 0.8)
        self.assertIn("node_2", self.node.connections)
        self.assertEqual(self.node.connections["node_2"]["relationship_type"], "semantic")
        self.assertEqual(self.node.connections["node_2"]["strength"], 0.8)

class TestKnowledgeGraphMemory(unittest.TestCase):
    def setUp(self):
        self.memory = KnowledgeGraphMemory(max_nodes=100)

    def test_store_memory(self):
        message = Message.create("neuron1", "Test memory content", 0.8)
        node_id = self.memory.store_memory(message)

        self.assertIn(node_id, self.memory.nodes)
        self.assertEqual(self.memory.nodes[node_id].content, "Test memory content")
        self.assertEqual(len(self.memory.temporal_index), 1)

    def test_retrieve_relevant_memories(self):
        # Store some test memories
        messages = [
            Message.create("neuron1", "The cat sat on the mat", 0.8),
            Message.create("neuron2", "Dogs are friendly animals", 0.7),
            Message.create("neuron3", "Cats and dogs can be pets", 0.9)
        ]

        for msg in messages:
            self.memory.store_memory(msg)

        # Search for cat-related memories
        results = self.memory.retrieve_relevant_memories("cat", limit=5)

        self.assertGreater(len(results), 0)
        # Should find memories containing "cat"
        cat_memories = [r for r in results if "cat" in r["content"].lower()]
        self.assertGreater(len(cat_memories), 0)

    def test_graph_relationships(self):
        # Store related memories
        msg1 = Message.create("neuron1", "Machine learning is powerful", 0.8)
        msg2 = Message.create("neuron2", "AI uses machine learning algorithms", 0.9)

        self.memory.store_memory(msg1)
        self.memory.store_memory(msg2)

        # Check that relationships were created
        nodes = list(self.memory.nodes.values())
        self.assertGreater(len(nodes), 1)

        # At least one node should have connections
        has_connections = any(len(node.connections) > 0 for node in nodes)
        self.assertTrue(has_connections)

    def test_get_recent_memories(self):
        # Store a few memories
        for i in range(3):
            msg = Message.create(f"neuron{i}", f"Memory content {i}", 0.8)
            self.memory.store_memory(msg)

        recent = self.memory.get_recent_memories(2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[-1]["content"], "Memory content 2")

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemoryManager(system=MemorySystem.GRAPH, max_nodes=100)

    def test_manager_initialization(self):
        self.assertEqual(self.manager.system, MemorySystem.GRAPH)
        self.assertIsNotNone(self.manager.memory_system)

    def test_store_and_retrieve(self):
        message = Message.create("test", "Test content", 0.8)
        address = self.manager.store_memory(message)

        self.assertIsNotNone(address)

        # Retrieve relevant memories
        results = self.manager.retrieve_relevant_memories("test", limit=5)
        self.assertGreater(len(results), 0)

    def test_system_switching(self):
        # Start with graph system
        self.assertEqual(self.manager.system, MemorySystem.GRAPH)

        # Switch to chain system
        self.manager.switch_system(MemorySystem.CHAIN, room_capacity=10)
        self.assertEqual(self.manager.system, MemorySystem.CHAIN)

        # Switch back
        self.manager.switch_system(MemorySystem.GRAPH, max_nodes=100)
        self.assertEqual(self.manager.system, MemorySystem.GRAPH)

if __name__ == '__main__':
    unittest.main()