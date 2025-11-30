"""
Attention-based Consensus: Advanced voting mechanism using neuron performance history.

This module implements attention-based voting where neurons are weighted
by their historical performance on similar tasks.
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class AttentionVoter:
    """
    Implements attention-based voting for consensus.
    
    Neurons with better historical performance get higher voting weight.
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """
        Initialize attention voter.
        
        Args:
            learning_rate: How quickly to update attention weights
        """
        self.neuron_weights: Dict[str, float] = defaultdict(lambda: 1.0)
        self.learning_rate = learning_rate
        self.history: List[Dict[str, Any]] = []
        
        logger.info("AttentionVoter initialized")
    
    def compute_attention_scores(self, messages: List[Any]) -> Dict[str, float]:
        """
        Compute attention scores for each neuron based on historical performance.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Dict mapping neuron name to attention score
        """
        scores = {}
        
        for msg in messages:
            neuron_name = msg.source
            base_weight = self.neuron_weights[neuron_name]
            confidence = msg.confidence
            
            # Attention score = historical weight * current confidence
            attention_score = base_weight * confidence
            scores[neuron_name] = attention_score
        
        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores
    
    def weighted_vote(self, messages: List[Any], attention_scores: Dict[str, float]) -> Any:
        """
        Select winning message using weighted voting.
        
        Args:
            messages: List of Message objects
            attention_scores: Attention scores for each neuron
            
        Returns:
            Winning message
        """
        # Group messages by content similarity (simple: exact match)
        content_groups = defaultdict(list)
        for msg in messages:
            # Use first 100 chars as key for grouping
            key = msg.content[:100].strip().lower()
            content_groups[key].append(msg)
        
        # Score each group by summing attention weights
        group_scores = {}
        for key, group in content_groups.items():
            total_weight = sum(attention_scores.get(msg.source, 0.0) for msg in group)
            avg_confidence = np.mean([msg.confidence for msg in group])
            
            # Combined score: attention weight * average confidence
            group_scores[key] = total_weight * avg_confidence
        
        # Select winning group
        if not group_scores:
            return messages[0] if messages else None
        
        winning_key = max(group_scores, key=group_scores.get)
        winning_group = content_groups[winning_key]
        
        # Within winning group, select highest confidence
        winner = max(winning_group, key=lambda m: m.confidence)
        
        return winner, {
            "method": "attention_weighted_vote",
            "winning_group_size": len(winning_group),
            "winning_score": group_scores[winning_key],
            "total_groups": len(content_groups),
            "attention_scores": attention_scores
        }
    
    def update_weights(self, neuron_name: str, performance_score: float):
        """
        Update attention weight for a neuron based on performance.
        
        Args:
            neuron_name: Name of the neuron
            performance_score: Score from -1.0 (bad) to 1.0 (good)
        """
        current_weight = self.neuron_weights[neuron_name]
        
        # Update: w_new = w_old + lr * score
        delta = self.learning_rate * performance_score
        new_weight = current_weight + delta
        
        # Clamp to reasonable range
        new_weight = max(0.1, min(3.0, new_weight))
        
        self.neuron_weights[neuron_name] = new_weight
        
        logger.debug(f"Updated attention weight for {neuron_name}: {current_weight:.2f} -> {new_weight:.2f}")
    
    def get_weights(self) -> Dict[str, float]:
        """Get current attention weights."""
        return dict(self.neuron_weights)


class HierarchicalConsensus:
    """
    Implements two-level consensus: fast thinking + slow thinking.
    
    Fast: Quick, low-confidence decisions
    Slow: Careful, high-confidence decisions
    """
    
    def __init__(self, fast_threshold: float = 0.7, slow_threshold: float = 0.9):
        """
        Initialize hierarchical consensus.
        
        Args:
            fast_threshold: Confidence threshold for fast decisions
            slow_threshold: Confidence threshold for slow decisions
        """
        self.fast_threshold = fast_threshold
        self.slow_threshold = slow_threshold
        
        logger.info(f"HierarchicalConsensus initialized (fast={fast_threshold}, slow={slow_threshold})")
    
    def decide(self, messages: List[Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make hierarchical decision.
        
        Args:
            messages: List of Message objects
            context: Optional context (e.g., urgency)
            
        Returns:
            Decision metadata
        """
        if not messages:
            return {"level": "none", "decision": None}
        
        # Calculate average confidence
        avg_confidence = np.mean([msg.confidence for msg in messages])
        
        # Check urgency from context
        urgency = context.get("urgency", 0.0) if context else 0.0
        
        # Decision logic
        if urgency > 0.8 or avg_confidence >= self.fast_threshold:
            # Fast thinking: use highest confidence message
            winner = max(messages, key=lambda m: m.confidence)
            return {
                "level": "fast",
                "decision": winner,
                "avg_confidence": avg_confidence,
                "reasoning": "High urgency or sufficient confidence for fast decision"
            }
        elif avg_confidence >= self.slow_threshold:
            # Slow thinking: more careful analysis (use clustering or attention)
            return {
                "level": "slow",
                "decision": None,  # Delegate to clustering/attention
                "avg_confidence": avg_confidence,
                "reasoning": "High confidence warrants careful slow thinking"
            }
        else:
            # Uncertain: request more information
            return {
                "level": "uncertain",
                "decision": None,
                "avg_confidence": avg_confidence,
                "reasoning": "Low confidence, need more information"
            }
