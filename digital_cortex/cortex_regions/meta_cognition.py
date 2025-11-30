"""
Meta-Cognition Layer: Self-monitoring and introspection system.

This module provides real-time monitoring of the system's cognitive state,
detecting confusion, uncertainty, and calibration errors.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CognitiveState:
    """Snapshot of the system's cognitive state."""
    confusion_level: float  # 0.0 to 1.0
    uncertainty_level: float  # 0.0 to 1.0
    is_stuck: bool
    needs_clarification: bool
    timestamp: str

class MetaCognitionLayer:
    """
    Monitors the system's thinking process for anomalies and improvement opportunities.
    """
    
    def __init__(self):
        self.history: List[CognitiveState] = []
        self.calibration_errors: List[Dict[str, Any]] = []
        
        # Thresholds
        self.confusion_threshold = 0.7
        self.uncertainty_threshold = 0.6
        
        logger.info("Meta-Cognition Layer initialized")
        
    def monitor_consensus(self, consensus_metadata: Dict[str, Any]) -> CognitiveState:
        """
        Analyze consensus results to detect confusion or uncertainty.
        
        Args:
            consensus_metadata: Metadata from CorpusColosseum.find_consensus()
            
        Returns:
            CognitiveState object
        """
        # Extract metrics
        cluster_count = consensus_metadata.get("cluster_count", 0)
        total_messages = consensus_metadata.get("total_messages", 0)
        winning_confidence = consensus_metadata.get("winning_cluster_avg_confidence", 0.0)
        selection_method = consensus_metadata.get("selection", "")
        
        # Calculate confusion (high fragmentation)
        # If many clusters relative to messages, neurons are disagreeing
        if total_messages > 1:
            fragmentation = (cluster_count - 1) / (total_messages - 1) if total_messages > 1 else 0
        else:
            fragmentation = 0.0
            
        confusion_level = fragmentation
        
        # Calculate uncertainty (low confidence or fallback selection)
        uncertainty_level = 1.0 - winning_confidence
        
        if selection_method == "highest_confidence_fallback":
            uncertainty_level = max(uncertainty_level, 0.8)  # High uncertainty if clustering failed
            confusion_level = max(confusion_level, 0.9)      # High confusion if no clusters formed
            
        # Determine if stuck or needs help
        is_stuck = confusion_level > self.confusion_threshold and uncertainty_level > self.uncertainty_threshold
        needs_clarification = uncertainty_level > 0.8
        
        state = CognitiveState(
            confusion_level=confusion_level,
            uncertainty_level=uncertainty_level,
            is_stuck=is_stuck,
            needs_clarification=needs_clarification,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.history.append(state)
        
        if is_stuck:
            logger.warning(f"System is STUCK (confusion={confusion_level:.2f}, uncertainty={uncertainty_level:.2f})")
            
        return state

    def check_calibration(self, prediction_confidence: float, outcome_score: float):
        """
        Check if confidence matches reality (calibration).
        
        Args:
            prediction_confidence: 0.0 to 1.0
            outcome_score: -1.0 (failure) to 1.0 (success)
        """
        # Normalize outcome to 0.0-1.0 for comparison
        normalized_outcome = (outcome_score + 1.0) / 2.0
        
        error = abs(prediction_confidence - normalized_outcome)
        
        # Detect significant miscalibration
        if error > 0.5:
            error_type = "overconfident" if prediction_confidence > normalized_outcome else "underconfident"
            
            record = {
                "type": error_type,
                "confidence": prediction_confidence,
                "outcome": normalized_outcome,
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.calibration_errors.append(record)
            logger.info(f"Calibration alert: System was {error_type} (conf={prediction_confidence:.2f}, outcome={normalized_outcome:.2f})")

    def get_status(self) -> Dict[str, Any]:
        """Get current meta-cognitive status."""
        status = {
            "calibration_alerts": len(self.calibration_errors)
        }
        
        if self.history:
            latest = self.history[-1]
            status.update({
                "confusion": latest.confusion_level,
                "uncertainty": latest.uncertainty_level,
                "is_stuck": latest.is_stuck,
                "status": "active"
            })
        else:
            status["status"] = "idle"
            
        return status
