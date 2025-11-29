"""
Amygdala: Threat and urgency assessment system.

The Amygdala evaluates situations for potential threats, urgency, and emotional valence.
It provides rapid threat assessment to guide decision-making processes.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..utils.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ThreatAssessment:
    """Result of a threat assessment."""
    threat_level: float  # 0.0 to 1.0 (0 = no threat, 1 = extreme threat)
    urgency: float       # 0.0 to 1.0 (0 = no rush, 1 = immediate action)
    valence: float       # -1.0 to 1.0 (negative to positive emotional context)
    confidence: float    # 0.0 to 1.0 (confidence in assessment)
    triggers: List[str]  # What triggered this assessment
    reasoning: str       # Brief explanation


class Amygdala:
    """
    Threat assessment and emotional processing system.

    Analyzes inputs for potential threats, urgency levels, and emotional valence.
    Provides rapid, instinctive responses to guide decision-making.
    """

    def __init__(self):
        """Initialize the Amygdala."""
        # Threat keywords organized by intensity levels
        self.threat_keywords = {
            'extreme': [
                'attack', 'danger', 'deadly', 'fatal', 'lethal', 'kill', 'death',
                'explosion', 'fire', 'poison', 'weapon', 'armed', 'hostile'
            ],
            'high': [
                'threat', 'risk', 'hazard', 'warning', 'alert', 'emergency',
                'intruder', 'suspicious', 'unusual', 'strange', 'unknown'
            ],
            'medium': [
                'caution', 'careful', 'watch', 'monitor', 'concern', 'worry',
                'uncertain', 'questionable', 'doubtful'
            ]
        }

        # Urgency indicators
        self.urgency_keywords = [
            'immediate', 'urgent', 'now', 'quickly', 'fast', 'rush', 'hurry',
            'emergency', 'critical', 'priority', 'asap'
        ]

        # Valence indicators (positive/negative emotional context)
        self.positive_keywords = [
            'safe', 'good', 'positive', 'happy', 'pleased', 'satisfied',
            'comfortable', 'relaxed', 'peaceful', 'friendly'
        ]

        self.negative_keywords = [
            'bad', 'negative', 'sad', 'angry', 'fear', 'anxiety', 'stress',
            'uncomfortable', 'tense', 'hostile', 'dangerous'
        ]

        # Pattern for detecting questions (uncertainty)
        self.question_pattern = re.compile(r'\?|what|how|why|when|where|who', re.IGNORECASE)

        logger.info("Amygdala initialized with threat assessment capabilities")

    def assess_threat(self, text: str, context: Optional[Dict[str, Any]] = None) -> ThreatAssessment:
        """
        Assess a text input for threats, urgency, and emotional valence.

        Args:
            text: The text to analyze
            context: Additional context information

        Returns:
            ThreatAssessment with detailed analysis
        """
        text_lower = text.lower()
        triggers = []

        # Assess threat level
        threat_score = 0.0
        threat_triggers = []

        # Check for extreme threats
        for keyword in self.threat_keywords['extreme']:
            if keyword in text_lower:
                threat_score += 0.9
                threat_triggers.append(f"extreme: {keyword}")

        # Check for high threats
        for keyword in self.threat_keywords['high']:
            if keyword in text_lower:
                threat_score += 0.6
                threat_triggers.append(f"high: {keyword}")

        # Check for medium threats
        for keyword in self.threat_keywords['medium']:
            if keyword in text_lower:
                threat_score += 0.3
                threat_triggers.append(f"medium: {keyword}")

        # Normalize threat score
        threat_level = min(1.0, threat_score)

        # Assess urgency
        urgency_score = 0.0
        urgency_triggers = []

        for keyword in self.urgency_keywords:
            if keyword in text_lower:
                urgency_score += 0.8
                urgency_triggers.append(keyword)

        # Questions can indicate uncertainty/need for assessment
        if self.question_pattern.search(text):
            urgency_score += 0.3
            urgency_triggers.append("question_detected")

        urgency = min(1.0, urgency_score)

        # Assess valence (emotional context)
        valence_score = 0.0
        valence_triggers = []

        # Positive indicators
        for keyword in self.positive_keywords:
            if keyword in text_lower:
                valence_score += 0.4
                valence_triggers.append(f"positive: {keyword}")

        # Negative indicators
        for keyword in self.negative_keywords:
            if keyword in text_lower:
                valence_score -= 0.4
                valence_triggers.append(f"negative: {keyword}")

        # Threat level influences valence negatively
        valence_score -= threat_level * 0.5

        valence = max(-1.0, min(1.0, valence_score))

        # Combine all triggers
        all_triggers = threat_triggers + urgency_triggers + valence_triggers

        # Calculate confidence based on trigger strength and text length
        base_confidence = min(0.9, len(text) / 200)  # Longer texts = more context
        trigger_confidence = min(0.8, len(all_triggers) * 0.2)  # More triggers = higher confidence
        confidence = (base_confidence + trigger_confidence) / 2

        # Generate reasoning
        reasoning_parts = []
        if threat_level > 0.5:
            reasoning_parts.append(f"High threat detected ({threat_level:.1f})")
        if urgency > 0.5:
            reasoning_parts.append(f"High urgency required ({urgency:.1f})")
        if abs(valence) > 0.3:
            emotion = "positive" if valence > 0 else "negative"
            reasoning_parts.append(f"{emotion.capitalize()} emotional context ({valence:.1f})")

        if not reasoning_parts:
            reasoning_parts.append("No significant threats or urgency detected")

        reasoning = "; ".join(reasoning_parts)

        assessment = ThreatAssessment(
            threat_level=threat_level,
            urgency=urgency,
            valence=valence,
            confidence=confidence,
            triggers=all_triggers,
            reasoning=reasoning
        )

        logger.info(f"Amygdala assessment: threat={threat_level:.2f}, urgency={urgency:.2f}, valence={valence:.2f}")
        return assessment

    def process_message(self, message: Message) -> Message:
        """
        Process a message through the Amygdala for threat assessment.

        Args:
            message: Input message to analyze

        Returns:
            Enhanced message with Amygdala assessment
        """
        # Assess the message content
        assessment = self.assess_threat(message.content)

        # Create enhanced content
        enhanced_content = message.content
        if assessment.threat_level > 0.3:
            enhanced_content += f" [AMYGDALA: Threat Level {assessment.threat_level:.1f}]"
        if assessment.urgency > 0.5:
            enhanced_content += f" [URGENCY: {assessment.urgency:.1f}]"

        # Add assessment to metadata
        enhanced_metadata = message.metadata.copy()
        enhanced_metadata["amygdala_assessment"] = {
            "threat_level": assessment.threat_level,
            "urgency": assessment.urgency,
            "valence": assessment.valence,
            "confidence": assessment.confidence,
            "triggers": assessment.triggers,
            "reasoning": assessment.reasoning
        }

        # Adjust message confidence based on Amygdala assessment
        # High threat + high confidence = higher overall confidence
        amygdala_influence = assessment.threat_level * assessment.confidence
        adjusted_confidence = min(1.0, message.confidence + amygdala_influence * 0.2)

        # Create new message with Amygdala processing
        amygdala_message = Message.create(
            source=f"Amygdala_{message.source}",
            content=enhanced_content,
            confidence=adjusted_confidence,
            metadata=enhanced_metadata
        )

        logger.info(f"Amygdala processed message from {message.source}: threat={assessment.threat_level:.2f}")
        return amygdala_message

    def get_emotional_state(self) -> Dict[str, Any]:
        """
        Get current emotional state summary.

        Returns:
            Dictionary with emotional state information
        """
        # In a more sophisticated implementation, this would track
        # emotional state over time and provide summary statistics
        return {
            "current_state": "calm",  # Placeholder
            "recent_assessments": 0,  # Would track recent assessments
            "average_threat_level": 0.0,  # Would be calculated from history
            "dominant_emotion": "neutral"  # Would be derived from valence history
        }

    def reset_state(self):
        """Reset emotional state (useful for new sessions)."""
        logger.info("Amygdala state reset")
        # In a more sophisticated implementation, this would clear
        # emotional state history and reset to baseline