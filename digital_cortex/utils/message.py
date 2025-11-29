"""Message protocol for inter-module communication."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional
import json


@dataclass
class Message:
    """
    Standard message format for communication between Digital Cortex components.
    
    Attributes:
        source: Agent/module initiating the message
        content: The core observation, proposal, or action
        confidence: Confidence/urgency score (0.0 to 1.0)
        timestamp: ISO format timestamp
        metadata: Optional additional data
    """
    source: str
    content: str
    confidence: float
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate message fields."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if not self.source:
            raise ValueError("Source cannot be empty")
        
        if not self.content:
            raise ValueError("Content cannot be empty")
    
    @classmethod
    def create(cls, source: str, content: str, confidence: float, 
               metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        Factory method to create a message with automatic timestamp.
        
        Args:
            source: Agent/module name
            content: Message content
            confidence: Confidence score (0.0-1.0)
            metadata: Optional additional data
            
        Returns:
            Message instance
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'
        return cls(
            source=source,
            content=content,
            confidence=confidence,
            timestamp=timestamp,
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        return f"Message(source={self.source}, confidence={self.confidence:.2f}, content={self.content[:50]}...)"
