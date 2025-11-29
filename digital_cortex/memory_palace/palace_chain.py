"""
Memory Palace Chain: Long-term episodic memory with sequential rooms.

This module implements the Memory Palace Chain with:
1. Sequential room chaining (Room 1 → Room 2 → ...)
2. Hash-based addressing within rooms
3. Chain traversal for "internal voice"
4. Integration with Corpus Colosseum outputs
"""

import sys
import os
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import logging

from .lattice import ChessCubeLattice, Tier2Lattice
from ..utils.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryRoom:
    """
    A single room in the Memory Palace Chain.
    Each room is an 8x8x8 lattice (512 locations).
    """
    
    def __init__(self, room_id: int, capacity: int = 512):
        """
        Initialize a memory room.
        
        Args:
            room_id: Sequential ID of this room
            capacity: Maximum number of memories (default 512 for 8x8x8)
        """
        self.room_id = room_id
        self.capacity = capacity
        self.lattice = ChessCubeLattice(size=8)  # Internal 3D structure
        self.tier2 = Tier2Lattice(size=8)        # Shadow lattice for meta-data
        self.created_at = datetime.utcnow().isoformat() + 'Z'
        
        # Storage
        self.memories: Dict[str, Dict[str, Any]] = {}  # coordinate -> memory
        self.memory_count = 0
        
        # Metadata
        self.context = ""  # What this room is about
        self.next_room_id: Optional[int] = None
        self.prev_room_id: Optional[int] = None
        
        logger.info(f"Created Memory Room #{room_id}")
    
    def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Store a memory in this room using hash-based addressing.
        
        Args:
            content: The memory content
            metadata: Additional metadata
            
        Returns:
            Coordinate key where memory was stored
        """
        if self.memory_count >= self.capacity:
            raise ValueError(f"Room #{self.room_id} is at capacity")
        
        # Hash-based coordinate assignment
        coords = self._hash_to_coords(content)
        coord_key = f"{coords[0]}_{coords[1]}_{coords[2]}"
        
        # Handle collisions by linear probing
        while coord_key in self.memories:
            coords = self._increment_coords(coords)
            coord_key = f"{coords[0]}_{coords[1]}_{coords[2]}"
        
        # Store memory
        memory_entry = {
            "content": content,
            "metadata": metadata,
            "coords": coords,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "room_id": self.room_id
        }
        
        self.memories[coord_key] = memory_entry
        self.memory_count += 1
        
        logger.debug(f"Stored memory at {coord_key} in Room #{self.room_id}")
        return coord_key
    
    def _hash_to_coords(self, content: str) -> Tuple[int, int, int]:
        """Convert content hash to 3D coordinates."""
        h = hash(content) % (8 * 8 * 8)
        x = (h // 64) + 1
        y = ((h % 64) // 8) + 1
        z = (h % 8) + 1
        return (x, y, z)
    
    def _increment_coords(self, coords: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Increment coordinates for collision handling."""
        x, y, z = coords
        z += 1
        if z > 8:
            z = 1
            y += 1
        if y > 8:
            y = 1
            x += 1
        if x > 8:
            x = 1
        return (x, y, z)
    
    def retrieve(self, coord_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory by coordinate."""
        return self.memories.get(coord_key)
    
    def is_full(self) -> bool:
        """Check if room is at capacity."""
        return self.memory_count >= self.capacity
    
    def get_state(self) -> Dict[str, Any]:
        """Get room state."""
        return {
            "room_id": self.room_id,
            "memory_count": self.memory_count,
            "capacity": self.capacity,
            "created_at": self.created_at,
            "context": self.context,
            "next_room_id": self.next_room_id,
            "prev_room_id": self.prev_room_id
        }


class MemoryPalaceChain:
    """
    Sequential chain of Memory Rooms forming the long-term episodic memory.
    
    The chain preserves the linear "internal voice" and autobiographical timeline.
    """
    
    def __init__(self, room_capacity: int = 512):
        """
        Initialize the Memory Palace Chain.
        
        Args:
            room_capacity: Capacity of each room (default 512)
        """
        self.room_capacity = room_capacity
        self.rooms: Dict[int, MemoryRoom] = {}
        self.current_room_id = 0
        self.total_memories = 0
        
        # Create first room
        self._create_room()
        
        logger.info("Memory Palace Chain initialized")
    
    def _create_room(self) -> MemoryRoom:
        """Create a new room and add it to the chain."""
        new_room_id = len(self.rooms)
        new_room = MemoryRoom(new_room_id, self.room_capacity)
        
        # Link to previous room
        if new_room_id > 0:
            prev_room = self.rooms[new_room_id - 1]
            prev_room.next_room_id = new_room_id
            new_room.prev_room_id = new_room_id - 1
        
        self.rooms[new_room_id] = new_room
        self.current_room_id = new_room_id
        
        logger.info(f"Created new room #{new_room_id} in chain")
        return new_room
    
    def store_memory(self, message: Message, outcome: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory from the Corpus Colosseum.
        
        Args:
            message: The consensus message to store
            outcome: Optional outcome/result data
            
        Returns:
            Full address (room_id:coord_key)
        """
        current_room = self.rooms[self.current_room_id]
        
        # Check if we need a new room
        if current_room.is_full():
            logger.info(f"Room #{self.current_room_id} full, creating new room")
            current_room = self._create_room()
        
        # Prepare memory content
        content = message.content
        metadata = {
            "source": message.source,
            "confidence": message.confidence,
            "timestamp": message.timestamp,
            "message_metadata": message.metadata,
            "outcome": outcome
        }
        
        # Store in current room
        coord_key = current_room.store(content, metadata)
        self.total_memories += 1
        
        # Full address
        address = f"{self.current_room_id}:{coord_key}"
        logger.info(f"Stored memory at {address}")
        
        return address
    
    def retrieve_memory(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by full address.
        
        Args:
            address: Format "room_id:coord_key"
            
        Returns:
            Memory entry or None
        """
        try:
            room_id_str, coord_key = address.split(":")
            room_id = int(room_id_str)
            
            if room_id not in self.rooms:
                return None
            
            return self.rooms[room_id].retrieve(coord_key)
        except (ValueError, KeyError):
            logger.error(f"Invalid address format: {address}")
            return None
    
    def traverse_forward(self, start_room: int = 0, max_rooms: int = 10) -> List[Dict[str, Any]]:
        """
        Traverse the chain forward (simulating internal voice).
        
        Args:
            start_room: Starting room ID
            max_rooms: Maximum rooms to traverse
            
        Returns:
            List of room states
        """
        traversal = []
        current_id = start_room
        count = 0
        
        while current_id is not None and count < max_rooms:
            if current_id in self.rooms:
                room = self.rooms[current_id]
                traversal.append(room.get_state())
                current_id = room.next_room_id
                count += 1
            else:
                break
        
        return traversal
    
    def traverse_backward(self, start_room: Optional[int] = None, max_rooms: int = 10) -> List[Dict[str, Any]]:
        """
        Traverse the chain backward (for learning branches).
        
        Args:
            start_room: Starting room ID (defaults to current)
            max_rooms: Maximum rooms to traverse
            
        Returns:
            List of room states in reverse order
        """
        if start_room is None:
            start_room = self.current_room_id
        
        traversal = []
        current_id = start_room
        count = 0
        
        while current_id is not None and count < max_rooms:
            if current_id in self.rooms:
                room = self.rooms[current_id]
                traversal.append(room.get_state())
                current_id = room.prev_room_id
                count += 1
            else:
                break
        
        return traversal
    
    def get_recent_memories(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories from the current room."""
        current_room = self.rooms[self.current_room_id]
        memories = list(current_room.memories.values())
        return memories[-count:] if len(memories) > count else memories
    
    def get_chain_summary(self) -> Dict[str, Any]:
        """Get summary of the entire chain."""
        return {
            "total_rooms": len(self.rooms),
            "current_room_id": self.current_room_id,
            "total_memories": self.total_memories,
            "room_capacity": self.room_capacity,
            "rooms": [room.get_state() for room in self.rooms.values()]
        }
    
    def __repr__(self) -> str:
        return f"MemoryPalaceChain(rooms={len(self.rooms)}, memories={self.total_memories})"
