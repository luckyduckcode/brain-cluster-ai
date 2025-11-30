"""
Confidence Scorer: Advanced confidence extraction and analysis.

This module provides robust confidence scoring for LLM outputs by combining:
1. Explicit confidence markers (e.g., [CONFIDENCE: 0.9])
2. Semantic analysis (hedging vs. certainty words)
3. Heuristic adjustments based on response length and structure
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """
    Evaluates the confidence of a text response using multiple signals.
    """
    
    def __init__(self):
        # Words that indicate uncertainty
        self.hedging_words = {
            'maybe', 'perhaps', 'possibly', 'might', 'could', 'unlikely',
            'unsure', 'doubtful', 'assuming', 'guess', 'speculate',
            'probably', 'potential', 'conceivably', 'it seems', 'it appears'
        }
        
        # Words that indicate certainty
        self.certainty_words = {
            'definitely', 'certainly', 'absolutely', 'undoubtedly', 'proven',
            'confirmed', 'guaranteed', 'obvious', 'clear', 'precise',
            'exact', 'surely', 'conclusive', 'verified'
        }
        
        # Regex patterns for explicit confidence
        self.explicit_patterns = [
            r'\[CONFIDENCE:\s*([0-9.]+)\]',
            r'\[confidence:\s*([0-9.]+)\]',
            r'CONFIDENCE:\s*([0-9.]+)',
            r'Confidence:\s*([0-9.]+)',
            r'confidence score:\s*([0-9.]+)',
        ]

    def score(self, text: str, default: float = 0.5) -> float:
        """
        Calculate a comprehensive confidence score for the text.
        
        Args:
            text: The text to analyze
            default: Default score if no signals found
            
        Returns:
            Float between 0.0 and 1.0
        """
        if not text:
            return 0.0
            
        # 1. Check for explicit confidence (highest priority)
        explicit_score = self._extract_explicit_confidence(text)
        if explicit_score is not None:
            # If explicit score exists, we trust it but verify it essentially matches the tone
            # For now, we'll just return it as the primary signal
            return explicit_score
            
        # 2. If no explicit score, use semantic analysis
        semantic_score = self._analyze_semantic_confidence(text)
        
        # 3. Combine with default if semantic signal is weak
        if semantic_score is None:
            return default
            
        return semantic_score

    def _extract_explicit_confidence(self, text: str) -> Optional[float]:
        """Extract confidence score from explicit markers."""
        for pattern in self.explicit_patterns:
            # Search from the end of the string backwards for better performance on long texts
            # and to prioritize the final verdict
            matches = list(re.finditer(pattern, text))
            if matches:
                # Take the last match as it's likely the final conclusion
                last_match = matches[-1]
                try:
                    val = float(last_match.group(1))
                    # Handle percentage (e.g. 95 -> 0.95)
                    if val > 1.0:
                        val = val / 100.0
                    return max(0.0, min(1.0, val))
                except ValueError:
                    continue
        return None

    def _analyze_semantic_confidence(self, text: str) -> float:
        """
        Analyze text for hedging and certainty markers.
        Returns a score centered around 0.5.
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 0.5
            
        hedge_count = sum(1 for word in words if word in self.hedging_words)
        certainty_count = sum(1 for word in words if word in self.certainty_words)
        
        # Base score
        score = 0.6  # Start slightly positive as LLMs are generally confident
        
        # Penalize for hedging (stronger penalty)
        score -= (hedge_count * 0.05)
        
        # Bonus for certainty (smaller bonus to avoid overconfidence)
        score += (certainty_count * 0.03)
        
        # Length penalty: extremely short responses might be dismissive or incomplete
        if len(words) < 5:
            score -= 0.1
            
        return max(0.1, min(0.95, score))

    def remove_confidence_tags(self, text: str) -> str:
        """Remove explicit confidence tags from text."""
        clean_text = text
        for pattern in self.explicit_patterns:
            clean_text = re.sub(pattern, '', clean_text)
        return clean_text.strip()
