"""
Knowledge Graph Memory: Graph-based episodic memory system.

This module implements a knowledge graph for long-term memory storage,
replacing the linear chain with a more sophisticated network structure.
"""

import sys
import os
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Set
from datetime import datetime
import json
import logging
from collections import defaultdict
import networkx as nx

from ..utils.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryNode:
    """
    A node in the knowledge graph representing a single memory.
    """

    def __init__(self, node_id: str, content: str, metadata: Dict[str, Any]):
        """
        Initialize a memory node.

        Args:
            node_id: Unique identifier for this node
            content: The memory content
            metadata: Additional metadata
        """
        self.node_id = node_id
        self.content = content
        self.metadata = metadata
        self.created_at = datetime.utcnow().isoformat() + 'Z'
        self.embedding: Optional[np.ndarray] = None

        # Graph relationships
        self.connections: Dict[str, Dict[str, Any]] = {}  # node_id -> relationship_data

        # Access tracking for importance scoring
        self.access_count = 0
        self.last_accessed = self.created_at
        self.importance_score = 1.0

    def add_connection(self, target_node_id: str, relationship_type: str,
                      strength: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a connection to another node.

        Args:
            target_node_id: ID of the target node
            relationship_type: Type of relationship (temporal, semantic, contextual, etc.)
            strength: Strength of the connection (0.0 to 1.0)
            metadata: Additional relationship metadata
        """
        self.connections[target_node_id] = {
            "relationship_type": relationship_type,
            "strength": strength,
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "metadata": metadata or {}
        }

    def update_access(self):
        """Update access tracking."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow().isoformat() + 'Z'
        # Importance increases with access frequency
        self.importance_score = min(5.0, self.importance_score + 0.1)

    def get_connections_by_type(self, relationship_type: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Get all connections of a specific type."""
        return [(node_id, data) for node_id, data in self.connections.items()
                if data["relationship_type"] == relationship_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "embedding": self.embedding.tolist() if self.embedding is not None else None,
            "connections": self.connections,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "importance_score": self.importance_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryNode':
        """Create node from dictionary."""
        node = cls(data["node_id"], data["content"], data["metadata"])
        node.created_at = data["created_at"]
        if data.get("embedding"):
            node.embedding = np.array(data["embedding"])
        node.connections = data["connections"]
        node.access_count = data.get("access_count", 0)
        node.last_accessed = data.get("last_accessed", node.created_at)
        node.importance_score = data.get("importance_score", 1.0)
        return node


class KnowledgeGraphMemory:
    """
    Graph-based memory system using NetworkX for relationship management.

    Features:
    - Semantic relationships between memories
    - Temporal connections (conversation flow)
    - Contextual associations
    - Importance-based retrieval
    - Graph traversal for associative recall
    """

    def __init__(self, max_nodes: int = 10000):
        """
        Initialize the knowledge graph memory.

        Args:
            max_nodes: Maximum number of nodes to store
        """
        self.max_nodes = max_nodes
        self.nodes: Dict[str, MemoryNode] = {}
        self.graph = nx.DiGraph()  # Directed graph for relationships

        # Indexing for efficient retrieval
        self.content_index: Dict[str, Set[str]] = defaultdict(set)  # word -> node_ids
        self.temporal_index: List[str] = []  # Chronological order

        # Conversation tracking
        self.current_conversation: List[str] = []
        self.conversation_count = 0

        logger.info("Knowledge Graph Memory initialized")

    def store_memory(self, message: Message, outcome: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a memory in the knowledge graph.

        Args:
            message: The consensus message to store
            outcome: Optional outcome/result data

        Returns:
            Node ID of the stored memory
        """
        # Generate unique node ID
        node_id = f"mem_{len(self.nodes)}_{int(datetime.utcnow().timestamp())}"

        # Prepare metadata
        metadata = {
            "source": message.source,
            "confidence": message.confidence,
            "timestamp": message.timestamp,
            "message_metadata": message.metadata,
            "outcome": outcome,
            "conversation_id": self.conversation_count
        }

        # Create node
        node = MemoryNode(node_id, message.content, metadata)
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.to_dict())

        # Update indexes
        self._update_content_index(node_id, message.content)
        self.temporal_index.append(node_id)

        # Create relationships
        self._create_relationships(node_id, message, outcome)

        # Maintain size limits
        if len(self.nodes) > self.max_nodes:
            self._prune_old_memories()

        logger.info(f"Stored memory node: {node_id}")
        return node_id

    def _update_content_index(self, node_id: str, content: str):
        """Update the content index for keyword search."""
        words = set(content.lower().split())
        for word in words:
            if len(word) > 2:  # Skip very short words
                self.content_index[word].add(node_id)

    def _create_relationships(self, node_id: str, message: Message, outcome: Optional[Dict[str, Any]]):
        """
        Create relationships between the new node and existing nodes.
        """
        node = self.nodes[node_id]

        # 1. Temporal relationships (conversation flow)
        if self.current_conversation:
            # Connect to previous messages in current conversation
            for prev_node_id in self.current_conversation[-3:]:  # Last 3 messages
                if prev_node_id in self.nodes:
                    strength = 0.8  # Strong temporal connection
                    node.add_connection(prev_node_id, "temporal_next", strength)
                    self.nodes[prev_node_id].add_connection(node_id, "temporal_prev", strength)
                    self.graph.add_edge(prev_node_id, node_id, relationship="temporal", strength=strength)

        # Add to current conversation
        self.current_conversation.append(node_id)

        # 2. Semantic relationships (content similarity)
        self._create_semantic_relationships(node_id, message.content)

        # 3. Outcome-based relationships
        if outcome and outcome.get("contributing_neurons"):
            for neuron in outcome["contributing_neurons"]:
                # Find recent memories from this neuron
                related_nodes = self._find_recent_nodes_by_source(neuron, limit=5)
                for related_id in related_nodes:
                    if related_id != node_id:
                        strength = 0.6
                        node.add_connection(related_id, "neuron_consensus", strength)
                        self.nodes[related_id].add_connection(node_id, "neuron_consensus", strength)
                        self.graph.add_edge(related_id, node_id, relationship="neuron", strength=strength)

        # 4. Contextual relationships (based on metadata)
        self._create_contextual_relationships(node_id, message.metadata)

    def _create_semantic_relationships(self, node_id: str, content: str):
        """Create semantic relationships based on content similarity."""
        node = self.nodes[node_id]

        # Find nodes with similar keywords
        content_words = set(content.lower().split())
        related_nodes = set()

        for word in content_words:
            if len(word) > 2:
                related_nodes.update(self.content_index[word])

        # Create connections to semantically related nodes
        for related_id in related_nodes:
            if related_id != node_id and related_id in self.nodes:
                # Calculate similarity score
                related_content = self.nodes[related_id].content.lower()
                related_words = set(related_content.split())
                similarity = len(content_words.intersection(related_words)) / len(content_words.union(related_words))

                if similarity > 0.2:  # Minimum similarity threshold
                    strength = min(1.0, similarity)
                    node.add_connection(related_id, "semantic", strength)
                    self.nodes[related_id].add_connection(node_id, "semantic", strength)
                    self.graph.add_edge(related_id, node_id, relationship="semantic", strength=strength)

    def _create_contextual_relationships(self, node_id: str, metadata: Dict[str, Any]):
        """Create relationships based on contextual metadata."""
        node = self.nodes[node_id]

        # Connect to memories with similar emotional context
        if "amygdala_assessment" in metadata:
            assessment = metadata["amygdala_assessment"]
            threat_level = assessment.get("threat_level", 0.0)
            urgency = assessment.get("urgency", 0.0)

            # Find memories with similar emotional context
            for other_id, other_node in self.nodes.items():
                if other_id != node_id:
                    other_metadata = other_node.metadata
                    if "amygdala_assessment" in other_metadata:
                        other_assessment = other_metadata["amygdala_assessment"]
                        other_threat = other_assessment.get("threat_level", 0.0)
                        other_urgency = other_assessment.get("urgency", 0.0)

                        # Emotional similarity
                        threat_diff = abs(threat_level - other_threat)
                        urgency_diff = abs(urgency - other_urgency)

                        if threat_diff < 0.3 and urgency_diff < 0.3:
                            strength = 0.7
                            node.add_connection(other_id, "emotional", strength)
                            self.nodes[other_id].add_connection(node_id, "emotional", strength)
                            self.graph.add_edge(other_id, node_id, relationship="emotional", strength=strength)

    def _find_recent_nodes_by_source(self, source: str, limit: int = 5) -> List[str]:
        """Find recent nodes from a specific source."""
        recent_nodes = []
        for node_id in reversed(self.temporal_index):
            if len(recent_nodes) >= limit:
                break
            if self.nodes[node_id].metadata.get("source") == source:
                recent_nodes.append(node_id)
        return recent_nodes

    def _prune_old_memories(self):
        """Remove least important old memories to maintain size limits."""
        if len(self.nodes) <= self.max_nodes:
            return

        # Sort nodes by importance score (lower first)
        nodes_by_importance = sorted(
            self.nodes.items(),
            key=lambda x: (x[1].importance_score, x[1].access_count)
        )

        # Remove least important nodes
        nodes_to_remove = nodes_by_importance[:len(self.nodes) - self.max_nodes]

        for node_id, _ in nodes_to_remove:
            self._remove_node(node_id)

        logger.info(f"Pruned {len(nodes_to_remove)} old memories")

    def _remove_node(self, node_id: str):
        """Remove a node and its connections."""
        if node_id not in self.nodes:
            return

        # Remove from indexes
        node = self.nodes[node_id]
        content_words = set(node.content.lower().split())
        for word in content_words:
            if node_id in self.content_index[word]:
                self.content_index[word].remove(node_id)

        if node_id in self.temporal_index:
            self.temporal_index.remove(node_id)

        if node_id in self.current_conversation:
            self.current_conversation.remove(node_id)

        # Remove from graph
        self.graph.remove_node(node_id)

        # Remove node
        del self.nodes[node_id]

    def retrieve_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories relevant to a query using graph-based search.

        Args:
            query: The search query
            limit: Maximum number of memories to return

        Returns:
            List of relevant memory dictionaries
        """
        relevant_memories = []

        # 1. Keyword-based retrieval
        query_words = set(query.lower().split())
        candidate_nodes = set()

        for word in query_words:
            if len(word) > 2:
                candidate_nodes.update(self.content_index[word])

        # 2. Score candidates by relevance
        scored_candidates = []
        for node_id in candidate_nodes:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.update_access()  # Track access

                # Calculate relevance score
                content_words = set(node.content.lower().split())
                overlap = len(query_words.intersection(content_words))
                total_words = len(query_words.union(content_words))

                if total_words > 0:
                    keyword_score = overlap / total_words
                else:
                    keyword_score = 0.0

                # Factor in importance and recency
                importance_factor = node.importance_score / 5.0  # Normalize to 0-1
                recency_factor = self._calculate_recency_factor(node.created_at)

                # Combined score
                total_score = (keyword_score * 0.6) + (importance_factor * 0.3) + (recency_factor * 0.1)

                scored_candidates.append((node_id, total_score))

        # Sort by score and get top candidates
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_candidates[:limit*2]  # Get more for graph expansion

        # 3. Graph-based expansion (find related memories)
        expanded_candidates = set()
        for node_id, score in top_candidates:
            expanded_candidates.add(node_id)
            # Add strongly connected nodes
            for neighbor in self.graph.neighbors(node_id):
                edge_data = self.graph.get_edge_data(node_id, neighbor)
                if edge_data and edge_data.get("strength", 0) > 0.5:
                    expanded_candidates.add(neighbor)

        # 4. Score expanded candidates
        final_candidates = []
        for node_id in expanded_candidates:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                # Calculate final score (with graph bonus)
                base_score = next((score for nid, score in scored_candidates if nid == node_id), 0.0)
                graph_bonus = len(list(self.graph.neighbors(node_id))) * 0.1  # Connectivity bonus
                final_score = min(1.0, base_score + graph_bonus)

                final_candidates.append((node_id, final_score))

        # Sort and return top results
        final_candidates.sort(key=lambda x: x[1], reverse=True)
        top_nodes = final_candidates[:limit]

        # Format results
        for node_id, relevance_score in top_nodes:
            node = self.nodes[node_id]
            memory_info = {
                "address": node_id,
                "content": node.content,
                "outcome": node.metadata.get("outcome", {}),
                "timestamp": node.created_at,
                "relevance_score": relevance_score,
                "source": node.metadata.get("source", "unknown"),
                "importance": node.importance_score,
                "connections": len(node.connections)
            }
            relevant_memories.append(memory_info)

        logger.info(f"Retrieved {len(relevant_memories)} relevant memories for query: {query[:50]}...")
        return relevant_memories

    def _calculate_recency_factor(self, created_at: str) -> float:
        """Calculate recency factor (0-1, higher for more recent)."""
        try:
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.utcnow().replace(tzinfo=created_time.tzinfo)
            hours_old = (now - created_time).total_seconds() / 3600

            # Exponential decay: recent memories get higher scores
            if hours_old < 1:
                return 1.0
            elif hours_old < 24:
                return 0.8
            elif hours_old < 168:  # 1 week
                return 0.6
            else:
                return 0.3
        except:
            return 0.5  # Default if parsing fails

    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories."""
        recent_nodes = self.temporal_index[-limit:] if len(self.temporal_index) > limit else self.temporal_index

        memories = []
        for node_id in recent_nodes:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                memories.append({
                    "address": node_id,
                    "content": node.content,
                    "outcome": node.metadata.get("outcome", {}),
                    "timestamp": node.created_at,
                    "source": node.metadata.get("source", "unknown")
                })

        return memories

    def get_memory_count(self) -> int:
        """Get total number of memories stored."""
        return len(self.nodes)

    def start_new_conversation(self):
        """Start a new conversation context."""
        self.conversation_count += 1
        self.current_conversation = []
        logger.info(f"Started new conversation #{self.conversation_count}")

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        return {
            "nodes": len(self.nodes),
            "edges": self.graph.number_of_edges(),
            "avg_degree": sum(dict(self.graph.degree()).values()) / len(self.nodes) if self.nodes else 0,
            "conversations": self.conversation_count,
            "current_conversation_length": len(self.current_conversation)
        }

    def save_to_file(self, filepath: str):
        """Save the knowledge graph to a file."""
        data = {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "temporal_index": self.temporal_index,
            "conversation_count": self.conversation_count,
            "current_conversation": self.current_conversation,
            "graph_stats": self.get_graph_stats()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved knowledge graph to {filepath}")

    def load_from_file(self, filepath: str):
        """Load the knowledge graph from a file."""
        if not os.path.exists(filepath):
            logger.warning(f"Knowledge graph file not found: {filepath}")
            return

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Restore nodes
        self.nodes = {}
        for node_id, node_data in data["nodes"].items():
            self.nodes[node_id] = MemoryNode.from_dict(node_data)

        # Restore graph
        self.graph = nx.DiGraph()
        for node_id, node in self.nodes.items():
            self.graph.add_node(node_id, **node.to_dict())
            for target_id, connection_data in node.connections.items():
                if target_id in self.nodes:  # Only add edges to existing nodes
                    self.graph.add_edge(node_id, target_id,
                                      relationship=connection_data["relationship_type"],
                                      strength=connection_data["strength"])

        # Restore indexes
        self.temporal_index = data.get("temporal_index", [])
        self.conversation_count = data.get("conversation_count", 0)
        self.current_conversation = data.get("current_conversation", [])

        # Rebuild content index
        self.content_index = defaultdict(set)
        for node_id, node in self.nodes.items():
            self._update_content_index(node_id, node.content)

        logger.info(f"Loaded knowledge graph from {filepath}: {len(self.nodes)} nodes")

    def __repr__(self) -> str:
        return f"KnowledgeGraphMemory(nodes={len(self.nodes)}, edges={self.graph.number_of_edges()})"