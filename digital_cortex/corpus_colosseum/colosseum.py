"""
Corpus Colosseum: Short-term working memory with multi-agent consensus.

This module implements parallel LLM-neuron processing with convergence algorithms
to achieve unified decision-making through weighted consensus.
"""

from typing import List, Dict, Any, Optional, Tuple
import asyncio
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict
import logging

from ..utils.message import Message
from .attention_consensus import AttentionVoter, HierarchicalConsensus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorpusColosseum:
    """
    Short-term working memory that processes multiple LLM outputs in parallel
    and uses convergence algorithms to find consensus.
    
    The Colosseum:
    1. Receives outputs from multiple LLM-neurons
    2. Maps them to a temporary vector space (lattice)
    3. Applies clustering (DBSCAN) to find convergence
    4. Selects the winning cluster based on density and confidence
    5. Resets after task completion
    """
    
    def __init__(self, 
                 embedding_dim: int = 384,
                 dbscan_eps: float = 0.3,
                 dbscan_min_samples: int = 2,
                 max_capacity: int = 100):
        """
        Initialize the Corpus Colosseum.
        
        Args:
            embedding_dim: Dimension of the embedding space
            dbscan_eps: DBSCAN epsilon parameter (max distance between samples)
            dbscan_min_samples: Minimum samples to form a cluster
            max_capacity: Maximum messages before forced reset
        """
        self.embedding_dim = embedding_dim
        self.dbscan_eps = dbscan_eps
        self.dbscan_min_samples = dbscan_min_samples
        self.max_capacity = max_capacity
        
        # Current state
        self.messages: List[Message] = []
        self.embeddings: List[np.ndarray] = []
        self.reset_count = 0
        
        # Advanced consensus mechanisms
        self.attention_voter = AttentionVoter()
        self.hierarchical = HierarchicalConsensus()
        
        logger.info(f"Corpus Colosseum initialized (dim={embedding_dim}, eps={dbscan_eps})")
    
    def add_message(self, message: Message, embedding: Optional[np.ndarray] = None):
        """
        Add a message from an LLM-neuron to the Colosseum.
        
        Args:
            message: Message object from a neuron
            embedding: Optional pre-computed embedding vector
        """
        if len(self.messages) >= self.max_capacity:
            logger.warning(f"Colosseum at capacity ({self.max_capacity}), forcing reset")
            self.reset()
        
        self.messages.append(message)
        
        # If no embedding provided, create a simple one from confidence and content hash
        if embedding is None:
            embedding = self._simple_embedding(message)
        
        self.embeddings.append(embedding)
        logger.debug(f"Added message from {message.source} (confidence={message.confidence:.2f})")
    
    def _simple_embedding(self, message: Message) -> np.ndarray:
        """
        Create a simple embedding from message content and confidence.
        
        In production, this should use a proper embedding model (e.g., sentence-transformers).
        For now, we use a hash-based approach for prototyping.
        """
        # Use hash of content for reproducibility
        content_hash = hash(message.content) % (2**32)
        np.random.seed(content_hash)
        
        # Generate random vector and scale by confidence
        embedding = np.random.randn(self.embedding_dim)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        embedding = embedding * message.confidence  # Scale by confidence
        
        return embedding
    
    def find_consensus(self, method: str = "auto", context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Message], Dict[str, Any]]:
        """
        Apply convergence algorithm to find consensus among messages.
        
        Args:
            method: Consensus method ("auto", "dbscan", "attention", "hierarchical")
            context: Optional context for decision-making (e.g., urgency)
        
        Returns:
            Tuple of (winning_message, metadata_dict)
            - winning_message: The message with highest consensus
            - metadata: Information about the clustering and decision
        """
        if len(self.messages) == 0:
            logger.warning("No messages in Colosseum")
            return None, {"error": "No messages"}
        
        if len(self.messages) == 1:
            logger.info("Only one message, returning it as consensus")
            return self.messages[0], {"cluster_count": 1, "method": "single"}
        
        # Auto-select method based on context and message count
        if method == "auto":
            if context and context.get("urgency", 0) > 0.7:
                method = "hierarchical"
            elif len(self.messages) <= 3:
                method = "attention"
            else:
                method = "dbscan"
        
        # Apply selected method
        if method == "attention":
            return self._attention_consensus(context)
        elif method == "hierarchical":
            return self._hierarchical_consensus(context)
        else:
            return self._dbscan_consensus()
    
    def _dbscan_consensus(self) -> Tuple[Optional[Message], Dict[str, Any]]:
        """Original DBSCAN clustering consensus."""
        # Convert embeddings to numpy array
        X = np.array(self.embeddings)
        
        # Apply DBSCAN clustering
        clustering = DBSCAN(eps=self.dbscan_eps, min_samples=self.dbscan_min_samples)
        labels = clustering.fit_predict(X)
        
        # Analyze clusters
        cluster_info = self._analyze_clusters(labels)
        
        # Select winning cluster
        winning_message, selection_info = self._select_winner(labels, cluster_info)
        
        metadata = {
            "cluster_count": len(cluster_info),
            "total_messages": len(self.messages),
            "method": "dbscan",
            "clusters": cluster_info,
            **selection_info
        }
        
        logger.info(f"Consensus found: {winning_message.source} (confidence={winning_message.confidence:.2f})")
        
        return winning_message, metadata
    
    def _analyze_clusters(self, labels: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """
        Analyze the clusters formed by DBSCAN.
        
        Returns:
            Dictionary mapping cluster_id -> cluster_info
        """
        cluster_info = defaultdict(lambda: {
            "messages": [],
            "avg_confidence": 0.0,
            "size": 0,
            "sources": []
        })
        
        for idx, label in enumerate(labels):
            if label == -1:  # Noise point
                continue
            
            message = self.messages[idx]
            cluster_info[label]["messages"].append(message)
            cluster_info[label]["sources"].append(message.source)
            cluster_info[label]["size"] += 1
        
        # Calculate average confidence for each cluster
        for cluster_id, info in cluster_info.items():
            if info["size"] > 0:
                confidences = [msg.confidence for msg in info["messages"]]
                info["avg_confidence"] = np.mean(confidences)
        
        return dict(cluster_info)
    
    def _select_winner(self, labels: np.ndarray, 
                       cluster_info: Dict[int, Dict[str, Any]]) -> Tuple[Message, Dict[str, Any]]:
        """
        Select the winning message based on cluster density and confidence.
        
        Strategy:
        1. Calculate score = cluster_size * avg_confidence
        2. Select cluster with highest score
        3. Within that cluster, select message with highest individual confidence
        """
        if not cluster_info:
            # All noise points, select highest confidence message
            best_idx = np.argmax([msg.confidence for msg in self.messages])
            best_message = self.messages[best_idx]
            return best_message, {
                "selection": "highest_confidence_fallback",
                "contributing_neurons": [best_message.source]
            }
        
        # Score each cluster
        cluster_scores = {}
        for cluster_id, info in cluster_info.items():
            # Score = size * avg_confidence (favors both consensus and confidence)
            cluster_scores[cluster_id] = info["size"] * info["avg_confidence"]
        
        # Select winning cluster
        winning_cluster_id = max(cluster_scores, key=cluster_scores.get)
        winning_cluster = cluster_info[winning_cluster_id]
        
        # Select best message from winning cluster
        winning_message = max(winning_cluster["messages"], key=lambda m: m.confidence)
        
        selection_info = {
            "winning_cluster_id": winning_cluster_id,
            "winning_cluster_size": winning_cluster["size"],
            "winning_cluster_avg_confidence": winning_cluster["avg_confidence"],
            "cluster_score": cluster_scores[winning_cluster_id],
            "contributing_neurons": winning_cluster["sources"],
            "selection": "cluster_consensus"
        }
        
        return winning_message, selection_info
    
    def reset(self):
        """Clear the Colosseum for the next task."""
        message_count = len(self.messages)
        self.messages.clear()
        self.embeddings.clear()
        self.reset_count += 1
        logger.info(f"Colosseum reset (#{self.reset_count}, cleared {message_count} messages)")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the Colosseum."""
        return {
            "message_count": len(self.messages),
            "reset_count": self.reset_count,
            "capacity": self.max_capacity,
            "sources": [msg.source for msg in self.messages]
        }
    
    def __repr__(self) -> str:
        return f"CorpusColosseum(messages={len(self.messages)}, resets={self.reset_count})"
    
    def _attention_consensus(self, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Message], Dict[str, Any]]:
        """
        Use attention-based voting for consensus.
        
        Args:
            context: Optional context information
            
        Returns:
            Tuple of (winning_message, metadata)
        """
        # Compute attention scores
        attention_scores = self.attention_voter.compute_attention_scores(self.messages)
        
        # Weighted vote
        winner, vote_metadata = self.attention_voter.weighted_vote(self.messages, attention_scores)
        
        metadata = {
            "method": "attention",
            "total_messages": len(self.messages),
            **vote_metadata
        }
        
        logger.info(f"Attention consensus: {winner.source} (score={vote_metadata['winning_score']:.2f})")
        return winner, metadata
    
    def _hierarchical_consensus(self, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Message], Dict[str, Any]]:
        """
        Use hierarchical (fast/slow) consensus.
        
        Args:
            context: Optional context with urgency info
            
        Returns:
            Tuple of (winning_message, metadata)
        """
        decision = self.hierarchical.decide(self.messages, context)
        
        if decision["level"] == "fast":
            # Fast decision made
            return decision["decision"], {
                "method": "hierarchical_fast",
                "total_messages": len(self.messages),
                **decision
            }
        elif decision["level"] == "slow":
            # Delegate to DBSCAN for careful analysis
            logger.info("Hierarchical: delegating to slow (DBSCAN) thinking")
            return self._dbscan_consensus()
        else:
            # Uncertain - return highest confidence with warning
            winner = max(self.messages, key=lambda m: m.confidence)
            return winner, {
                "method": "hierarchical_uncertain",
                "total_messages": len(self.messages),
                "warning": "Low confidence, consider requesting more information",
                **decision
            }
    
    def get_attention_weights(self) -> Dict[str, float]:
        """Get current attention weights for all neurons."""
        return self.attention_voter.get_weights()
    
    def update_neuron_performance(self, neuron_name: str, performance_score: float):
        """
        Update attention weights based on neuron performance.
        
        Args:
            neuron_name: Name of the neuron
            performance_score: Score from -1.0 to 1.0
        """
        self.attention_voter.update_weights(neuron_name, performance_score)
