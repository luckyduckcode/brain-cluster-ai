"""
Consolidator: Reorganizes and optimizes memory during sleep.

This module implements 'Learning Branches' - backward traversal to find patterns
and optimize memory placement.
"""

import logging
from typing import List, Dict, Any
from collections import Counter
from ..memory_palace.palace_chain import MemoryPalaceChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Consolidator:
    """
    Optimizes the Memory Palace by analyzing usage patterns and restructuring.
    """
    
    def __init__(self, memory_chain: MemoryPalaceChain):
        self.chain = memory_chain
        
    def consolidate(self) -> Dict[str, Any]:
        """
        Perform memory consolidation.
        
        1. Analyze recent memories for patterns
        2. Identify frequent topics/keywords
        3. Generate a summary (meta-memory)
        
        Returns:
            Report of consolidation actions
        """
        logger.info("Starting Memory Consolidation...")
        
        # 1. Backward traversal (Review recent history)
        recent_history = self.chain.traverse_backward(max_rooms=5)
        
        if not recent_history:
            return {"status": "no_memories"}
            
        # 2. Extract content
        all_content = []
        for room_state in recent_history:
            room_id = room_state['room_id']
            if room_id in self.chain.rooms:
                room = self.chain.rooms[room_id]
                for mem in room.memories.values():
                    all_content.append(mem['content'])
        
        # 3. Find patterns (Simple word frequency for prototype)
        # In production, this would use LLM for semantic clustering
        words = " ".join(all_content).lower().split()
        common_words = Counter(words).most_common(5)
        
        # 4. Create Meta-Memory (Summary)
        summary = f"Consolidation Summary: Frequent themes include {', '.join([w[0] for w in common_words])}"
        
        # Store this summary in the current room (or a special 'Long Term' room)
        # For now, we just store it in the current room
        msg_mock = type('obj', (object,), {
            'content': summary,
            'source': 'Consolidator',
            'confidence': 1.0,
            'timestamp': 'now',
            'metadata': {'type': 'meta_memory'}
        })
        
        addr = self.chain.store_memory(msg_mock)
        
        logger.info(f"Consolidation complete. Created meta-memory at {addr}")
        
        return {
            "status": "success",
            "analyzed_rooms": len(recent_history),
            "meta_memory_address": addr,
            "themes": common_words
        }
