"""
Weight Learner: Adjusts neuron confidence based on outcomes.

This module implements the reinforcement learning aspect, updating
confidence scores for neurons that contribute to successful outcomes.
"""

from typing import Dict, Any, List
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeightLearner:
    """
    Manages confidence weights for neurons.
    """
    
    def __init__(self, storage_path: str = "neuron_weights.json"):
        """
        Initialize Weight Learner.
        
        Args:
            storage_path: Path to store persistent weights
        """
        self.storage_path = storage_path
        self.weights: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []
        
        # Load existing weights
        self._load_weights()
        
        logger.info(f"Weight Learner initialized (loaded {len(self.weights)} weights)")
    
    def update(self, neuron_name: str, score: float, learning_rate: float = 0.1):
        """
        Update weight for a neuron based on outcome score.
        
        Args:
            neuron_name: Name of the neuron
            score: Outcome score (-1.0 to 1.0)
            learning_rate: How fast to adapt (0.0 to 1.0)
        """
        current_weight = self.weights.get(neuron_name, 1.0)
        
        # Simple update rule: weight += learning_rate * score
        # But clamped to prevent runaway values
        delta = learning_rate * score
        new_weight = current_weight + delta
        
        # Clamp between 0.1 and 2.0 (never fully disable, never too dominant)
        new_weight = max(0.1, min(2.0, new_weight))
        
        self.weights[neuron_name] = new_weight
        
        # Record history
        self.history.append({
            "neuron": neuron_name,
            "old_weight": current_weight,
            "score": score,
            "new_weight": new_weight
        })
        
        logger.info(f"Updated weight for {neuron_name}: {current_weight:.2f} -> {new_weight:.2f} (score={score})")
        
        # Auto-save
        self._save_weights()
    
    def update_contributing_neurons(self, neuron_names: List[str], score: float, 
                                   learning_rate: float = 0.1):
        """
        Update weights for multiple neurons that contributed to a decision.
        
        Implements temporal credit assignment - all neurons in the winning
        cluster share the credit/blame proportionally.
        
        Args:
            neuron_names: List of neuron names that contributed to the decision
            score: Outcome score (-1.0 to 1.0) 
            learning_rate: How fast to adapt (0.0 to 1.0)
        """
        if not neuron_names:
            logger.warning("No neurons provided for update")
            return
            
        # Each contributing neuron gets the full score (they all contributed equally)
        # In more sophisticated implementations, this could be weighted by confidence
        for neuron_name in neuron_names:
            self.update(neuron_name, score, learning_rate)
    
    def get_weight(self, neuron_name: str) -> float:
        """Get current weight for a neuron."""
        return self.weights.get(neuron_name, 1.0)
    
    def _load_weights(self):
        """Load weights from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.weights = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load weights: {e}")
    
    def _save_weights(self):
        """Save weights to disk."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.weights, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save weights: {e}")
