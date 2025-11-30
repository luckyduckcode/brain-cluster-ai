"""
Message system for digital body communication.

Handles communication between sensory, motor, nervous, and brain systems.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class BodyMessage:
    """Message format for body system communication."""

    message_type: str  # 'sensory', 'motor', 'nervous', 'reflex'
    sensor_type: Optional[str] = None  # 'vision', 'audio', 'text', 'system'
    motor_type: Optional[str] = None   # 'speech', 'display', 'action'
    nervous_type: Optional[str] = None # 'proprioception', 'pain', 'pleasure', 'homeostasis'
    data: Dict[str, Any] = None
    confidence: float = 1.0
    timestamp: str = None
    source: str = "body"
    priority: int = 0  # 0=normal, 1=high, 2=critical

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.data is None:
            self.data = {}

    @classmethod
    def create_sensory(cls, sensor_type: str, data: Dict[str, Any],
                      confidence: float = 1.0, priority: int = 0) -> 'BodyMessage':
        """Create a sensory message."""
        return cls(
            message_type="sensory",
            sensor_type=sensor_type,
            data=data,
            confidence=confidence,
            priority=priority
        )

    @classmethod
    def create_motor(cls, motor_type: str, data: Dict[str, Any],
                    confidence: float = 1.0, priority: int = 0) -> 'BodyMessage':
        """Create a motor message."""
        return cls(
            message_type="motor",
            motor_type=motor_type,
            data=data,
            confidence=confidence,
            priority=priority
        )

    @classmethod
    def create_nervous(cls, nervous_type: str, data: Dict[str, Any],
                       confidence: float = 1.0, priority: int = 0) -> 'BodyMessage':
        """Create a nervous system message."""
        return cls(
            message_type="nervous",
            nervous_type=nervous_type,
            data=data,
            confidence=confidence,
            priority=priority
        )

    @classmethod
    def create_reflex(cls, reflex_type: str, data: Dict[str, Any],
                     priority: int = 2) -> 'BodyMessage':
        """Create a reflex message (high priority)."""
        return cls(
            message_type="reflex",
            data=data,
            priority=priority,
            source="reflex_system"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BodyMessage':
        """Create from dictionary."""
        return cls(**data)

    def __str__(self) -> str:
        return f"BodyMessage({self.message_type}:{self.sensor_type or self.motor_type or self.nervous_type}, priority={self.priority})"