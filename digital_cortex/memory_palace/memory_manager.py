"""
Memory Manager: Unified interface for different memory systems.

This module provides a unified interface that can use either the traditional
MemoryPalaceChain or the new KnowledgeGraphMemory system.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from .palace_chain import MemoryPalaceChain
from .knowledge_graph import KnowledgeGraphMemory
from ..utils.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemorySystem(Enum):
    """Available memory systems."""
    CHAIN = "chain"
    GRAPH = "graph"


class MemoryManager:
    """
    Unified memory manager that can use different memory systems.

    Provides a consistent interface while allowing switching between
    traditional chain-based and modern graph-based memory systems.
    """

    def __init__(self, system: MemorySystem = MemorySystem.GRAPH, **kwargs):
        """
        Initialize the memory manager.

        Args:
            system: Which memory system to use
            **kwargs: System-specific parameters
        """
        self.system = system
        self.memory_system = None

        if system == MemorySystem.CHAIN:
            room_capacity = kwargs.get('room_capacity', 512)
            self.memory_system = MemoryPalaceChain(room_capacity=room_capacity)
        elif system == MemorySystem.GRAPH:
            max_nodes = kwargs.get('max_nodes', 10000)
            self.memory_system = KnowledgeGraphMemory(max_nodes=max_nodes)
        else:
            raise ValueError(f"Unknown memory system: {system}")

        logger.info(f"Memory Manager initialized with {system.value} system")

    def store_memory(self, message: Message, outcome: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory using the current system.

        Args:
            message: The consensus message to store
            outcome: Optional outcome/result data

        Returns:
            Memory address/ID
        """
        return self.memory_system.store_memory(message, outcome)

    def retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to a query.

        Args:
            query: The search query
            limit: Maximum number of memories to return

        Returns:
            List of relevant memory dictionaries
        """
        if hasattr(self.memory_system, 'retrieve_relevant_memories'):
            return self.memory_system.retrieve_relevant_memories(query, limit)
        else:
            # Fallback for systems without semantic search
            return self.memory_system.get_recent_memories(limit)

    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories."""
        return self.memory_system.get_recent_memories(limit)

    def get_memory_count(self) -> int:
        """Get total number of memories stored."""
        if hasattr(self.memory_system, 'get_memory_count'):
            return self.memory_system.get_memory_count()
        else:
            # For chain system
            summary = self.memory_system.get_chain_summary()
            return summary.get('total_memories', 0)

    def start_new_conversation(self):
        """Start a new conversation context (graph system only)."""
        if hasattr(self.memory_system, 'start_new_conversation'):
            self.memory_system.start_new_conversation()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        stats = {
            "system": self.system.value,
            "memory_count": self.get_memory_count()
        }

        if hasattr(self.memory_system, 'get_graph_stats'):
            stats.update(self.memory_system.get_graph_stats())
        elif hasattr(self.memory_system, 'get_chain_summary'):
            chain_summary = self.memory_system.get_chain_summary()
            stats.update({
                "total_rooms": chain_summary.get('total_rooms', 0),
                "current_room_id": chain_summary.get('current_room_id', 0),
                "room_capacity": chain_summary.get('room_capacity', 0)
            })

        return stats

    def save_to_file(self, filepath: str):
        """Save the memory system to a file."""
        if hasattr(self.memory_system, 'save_to_file'):
            self.memory_system.save_to_file(filepath)
        else:
            logger.warning(f"Save not supported for {self.system.value} system")

    def load_from_file(self, filepath: str):
        """Load the memory system from a file."""
        if hasattr(self.memory_system, 'load_from_file'):
            self.memory_system.load_from_file(filepath)
        else:
            logger.warning(f"Load not supported for {self.system.value} system")

    def switch_system(self, new_system: MemorySystem, **kwargs):
        """
        Switch to a different memory system.

        Warning: This will migrate existing memories if possible.

        Args:
            new_system: The new memory system to use
            **kwargs: Parameters for the new system
        """
        logger.info(f"Switching from {self.system.value} to {new_system.value} system")

        # Save current state
        temp_file = f"/tmp/memory_migration_{self.system.value}_to_{new_system.value}.json"
        self.save_to_file(temp_file)

        # Create new system
        old_system = self.system
        self.system = new_system

        if new_system == MemorySystem.CHAIN:
            room_capacity = kwargs.get('room_capacity', 512)
            self.memory_system = MemoryPalaceChain(room_capacity=room_capacity)
        elif new_system == MemorySystem.GRAPH:
            max_nodes = kwargs.get('max_nodes', 10000)
            self.memory_system = KnowledgeGraphMemory(max_nodes=max_nodes)

        # Try to load migrated data
        try:
            self.load_from_file(temp_file)
            logger.info("Successfully migrated memory data")
        except Exception as e:
            logger.error(f"Failed to migrate memory data: {e}")
            # Revert to old system
            self.system = old_system
            if old_system == MemorySystem.CHAIN:
                self.memory_system = MemoryPalaceChain()
            elif old_system == MemorySystem.GRAPH:
                self.memory_system = KnowledgeGraphMemory()

        # Clean up
        try:
            os.remove(temp_file)
        except:
            pass

    def __repr__(self) -> str:
        return f"MemoryManager(system={self.system.value}, memories={self.get_memory_count()})"