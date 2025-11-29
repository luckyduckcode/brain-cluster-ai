"""
Dreamer: Generates creative connections through controlled hallucination.

This module implements 'Dream Branches' - random walks through the Memory Palace
that explore novel connections between disparate memories.
"""

import random
import logging
from typing import List, Dict, Any, Optional
from ..memory_palace.palace_chain import MemoryPalaceChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Dreamer:
    """
    Explores the Memory Palace during sleep cycles to find novel connections.
    """
    
    def __init__(self, memory_chain: MemoryPalaceChain):
        """
        Initialize the Dreamer.
        
        Args:
            memory_chain: The Memory Palace Chain to dream in
        """
        self.chain = memory_chain
        self.dream_log: List[Dict[str, Any]] = []
        
    def dream(self, start_room_id: Optional[int] = None, steps: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a random walk (dream) through the memory chain.
        
        Args:
            start_room_id: Where to start dreaming (None = random room)
            steps: How many steps to take in the dream
            
        Returns:
            List of memories encountered in the dream
        """
        logger.info("Entering REM sleep (Dreaming)...")
        
        # Pick start room
        if start_room_id is None:
            if not self.chain.rooms:
                logger.warning("No rooms to dream in!")
                return []
            start_room_id = random.choice(list(self.chain.rooms.keys()))
            
        current_room_id = start_room_id
        dream_sequence = []
        
        for i in range(steps):
            if current_room_id not in self.chain.rooms:
                break
                
            room = self.chain.rooms[current_room_id]
            
            # 1. Pick a random memory in this room
            if not room.memories:
                logger.debug(f"Room {current_room_id} is empty, moving on")
            else:
                memory_key = random.choice(list(room.memories.keys()))
                memory = room.memories[memory_key]
                dream_sequence.append({
                    "step": i,
                    "room_id": current_room_id,
                    "content": memory["content"],
                    "type": "memory_recall"
                })
            
            # 2. Decide where to go next (Random Walk)
            # Options: Next Room, Prev Room, or Stay (and jump to random coord)
            move = random.choice(["next", "prev", "stay"])
            
            if move == "next" and room.next_room_id is not None:
                current_room_id = room.next_room_id
            elif move == "prev" and room.prev_room_id is not None:
                current_room_id = room.prev_room_id
            else:
                # Stay in room but maybe hallucinate a connection
                if len(dream_sequence) > 1:
                    prev_mem = dream_sequence[-2]
                    curr_mem = dream_sequence[-1]
                    
                    # Simple "hallucination": Combine two memories
                    hallucination = f"Dream connection: {prev_mem['content']} <--> {curr_mem['content']}"
                    dream_sequence.append({
                        "step": i,
                        "room_id": current_room_id,
                        "content": hallucination,
                        "type": "hallucination"
                    })
        
        self.dream_log.append({
            "timestamp": "now",
            "sequence": dream_sequence
        })
        
        logger.info(f"Dream complete ({len(dream_sequence)} items)")
        return dream_sequence
