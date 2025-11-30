"""
Semantic Cache: LRU cache with semantic similarity matching.

This module provides caching for LLM responses based on semantic similarity
of prompts, avoiding redundant API calls for similar queries.
"""

import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    LRU cache with semantic similarity matching for LLM responses.
    
    Uses simple string hashing for now, but can be extended with
    embedding-based similarity in the future.
    """
    
    def __init__(self, max_size: int = 100, similarity_threshold: float = 0.95):
        """
        Initialize the semantic cache.
        
        Args:
            max_size: Maximum number of cached items
            similarity_threshold: Threshold for considering prompts similar (0.0-1.0)
        """
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0
        
        logger.info(f"Semantic cache initialized (max_size={max_size})")
    
    def _compute_key(self, prompt: str, model: str, temperature: float) -> str:
        """Compute cache key from prompt and parameters."""
        # Normalize prompt (strip whitespace, lowercase for better matching)
        normalized = prompt.strip().lower()
        
        # Create composite key - temperature rounded to avoid float precision issues
        temp_rounded = round(temperature, 2)
        composite = f"{model}:{temp_rounded}:{normalized}"
        
        # Hash for consistent key length
        return hashlib.sha256(composite.encode()).hexdigest()
    
    def _compute_similarity(self, prompt1: str, prompt2: str) -> float:
        """
        Compute similarity between two prompts.
        
        Currently uses simple string matching. Can be upgraded to:
        - Levenshtein distance
        - Embedding cosine similarity
        - Fuzzy matching
        """
        p1 = prompt1.strip().lower()
        p2 = prompt2.strip().lower()
        
        # Exact match
        if p1 == p2:
            return 1.0
        
        # Simple word overlap similarity
        words1 = set(p1.split())
        words2 = set(p2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get(self, prompt: str, model: str, temperature: float) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available.
        
        Args:
            prompt: Input prompt
            model: Model name
            temperature: Temperature parameter
            
        Returns:
            Cached response dict or None
        """
        key = self._compute_key(prompt, model, temperature)
        
        # Check for exact match first
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry = self.cache[key]
            logger.debug(f"Cache HIT (exact): {prompt[:50]}...")
            return entry["response"]
        
        # Check for semantic similarity (only if model and temp match)
        for cached_key, entry in self.cache.items():
            # Must have same model and temperature for similarity check
            if entry["model"] != model or round(entry["temperature"], 2) != round(temperature, 2):
                continue
                
            similarity = self._compute_similarity(prompt, entry["prompt"])
            if similarity >= self.similarity_threshold:
                self.hits += 1
                # Move to end
                self.cache.move_to_end(cached_key)
                logger.debug(f"Cache HIT (similar {similarity:.2f}): {prompt[:50]}...")
                return entry["response"]
        
        self.misses += 1
        logger.debug(f"Cache MISS: {prompt[:50]}...")
        return None
    
    def put(self, prompt: str, model: str, temperature: float, response: Dict[str, Any]):
        """
        Store response in cache.
        
        Args:
            prompt: Input prompt
            model: Model name
            temperature: Temperature parameter
            response: Response to cache
        """
        key = self._compute_key(prompt, model, temperature)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = next(iter(self.cache))
            self.cache.pop(oldest_key)
            logger.debug(f"Cache evicted oldest entry")
        
        # Store entry
        self.cache[key] = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        logger.debug(f"Cache stored: {prompt[:50]}...")
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total
        }
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"SemanticCache(size={stats['size']}/{stats['max_size']}, hit_rate={stats['hit_rate']:.2%})"
