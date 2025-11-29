"""
Sensorium: Sensory processing cortex for the Digital Cortex.

The Sensorium processes external inputs (text, images, environment) and converts
them into standardized messages for the neural network.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..utils.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Sensorium:
    """
    Sensory processing unit that handles text, image, and environmental inputs.

    Converts raw inputs into standardized Message objects for the neural network.
    """

    def __init__(self):
        """Initialize the Sensorium."""
        logger.info("Sensorium initialized")

    def process_text(self, text: str, source: str = "text_input",
                    metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Process text input and create a standardized message.

        Args:
            text: The text content to process
            source: Source identifier for the message
            metadata: Additional metadata about the text

        Returns:
            Message object with processed text information
        """
        # Basic text analysis
        text_info = self._analyze_text(text)

        # Create comprehensive content description
        content = f"Text input processed: {text[:100]}{'...' if len(text) > 100 else ''}"
        if text_info['word_count'] > 0:
            content += f" ({text_info['word_count']} words, {text_info['sentence_count']} sentences)"

        # Add metadata
        message_metadata = {
            "sensorium_type": "text",
            "text_analysis": text_info,
            "original_text": text[:500],  # Truncate for storage
            **(metadata or {})
        }

        # Create message with confidence based on text quality
        confidence = min(0.9, max(0.3, len(text) / 1000))  # Higher confidence for longer, coherent text

        message = Message.create(
            source=f"Sensorium_{source}",
            content=content,
            confidence=confidence,
            metadata=message_metadata
        )

        logger.info(f"Processed text input: {text_info['word_count']} words, confidence {confidence:.2f}")
        return message

    def process_image(self, image_path: str, source: str = "image_input",
                     metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Process image input and create a standardized message.

        Args:
            image_path: Path to the image file
            source: Source identifier for the message
            metadata: Additional metadata about the image

        Returns:
            Message object with processed image information
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Basic image analysis (without heavy ML libraries for now)
        image_info = self._analyze_image_basic(image_path)

        # Create content description
        content = f"Image processed: {image_info['filename']} ({image_info['file_size_kb']}KB)"
        if 'dimensions' in image_info:
            content += f", {image_info['dimensions'][0]}x{image_info['dimensions'][1]} pixels"

        # Add visual features if available
        if image_info.get('basic_features'):
            features = image_info['basic_features']
            content += f", appears to contain: {', '.join(features)}"

        # Add metadata
        message_metadata = {
            "sensorium_type": "image",
            "image_analysis": image_info,
            "file_path": image_path,
            **(metadata or {})
        }

        # Create message with moderate confidence for basic analysis
        confidence = 0.6  # Could be improved with actual CV models

        message = Message.create(
            source=f"Sensorium_{source}",
            content=content,
            confidence=confidence,
            metadata=message_metadata
        )

        logger.info(f"Processed image: {image_path}, confidence {confidence:.2f}")
        return message

    def capture_environment_state(self, context: str = "general",
                                 metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Capture current environment/computer state.

        Args:
            context: Context for the state capture (e.g., "before_action", "after_action")
            metadata: Additional metadata

        Returns:
            Message object with environment state information
        """
        # Capture basic system information
        env_info = self._capture_system_info()

        content = f"Environment state captured ({context}): {env_info['os']}, {env_info['cpu_count']} CPUs"

        # Add relevant state information
        if context == "before_action":
            content += ". Preparing for action execution."
        elif context == "after_action":
            content += ". Action completed, assessing results."

        message_metadata = {
            "sensorium_type": "environment",
            "environment_info": env_info,
            "capture_context": context,
            **(metadata or {})
        }

        # High confidence for system state capture
        confidence = 0.95

        message = Message.create(
            source=f"Sensorium_Environment_{context}",
            content=content,
            confidence=confidence,
            metadata=message_metadata
        )

        logger.info(f"Captured environment state for context: {context}")
        return message

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Basic text analysis."""
        words = text.split()
        sentences = text.split('.')

        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "character_count": len(text),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "contains_questions": '?' in text,
            "contains_exclamations": '!' in text,
            "is_all_caps": text.isupper() and len(text) > 10,
            "is_all_lowercase": text.islower() and len(text) > 10
        }

    def _analyze_image_basic(self, image_path: str) -> Dict[str, Any]:
        """Basic image analysis without ML libraries."""
        import imghdr

        info = {
            "filename": os.path.basename(image_path),
            "file_size_kb": round(os.path.getsize(image_path) / 1024, 2),
            "file_type": imghdr.what(image_path) or "unknown"
        }

        # Try to get dimensions (works for common formats)
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                info["dimensions"] = img.size
                info["mode"] = img.mode
                info["format"] = img.format

                # Very basic feature detection
                if img.mode == 'RGB':
                    # Check for dominant colors (very simplistic)
                    img_small = img.resize((10, 10))
                    colors = img_small.getcolors(100)
                    if colors:
                        # Sort by frequency
                        colors.sort(key=lambda x: x[0], reverse=True)
                        dominant_color = colors[0][1]

                        # Very basic color classification
                        r, g, b = dominant_color
                        if r > 200 and g < 100 and b < 100:
                            info["basic_features"] = ["red dominant"]
                        elif g > 200 and r < 100 and b < 100:
                            info["basic_features"] = ["green dominant"]
                        elif b > 200 and r < 100 and g < 100:
                            info["basic_features"] = ["blue dominant"]
                        else:
                            info["basic_features"] = ["mixed colors"]
        except ImportError:
            logger.warning("PIL not available, skipping advanced image analysis")
            info["basic_features"] = ["analysis limited - PIL not available"]
        except Exception as e:
            logger.warning(f"Error analyzing image: {e}")
            info["basic_features"] = ["analysis failed"]

        return info

    def _capture_system_info(self) -> Dict[str, Any]:
        """Capture basic system information."""
        import platform
        import psutil

        try:
            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "cpu_count": os.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                "python_version": platform.python_version()
            }
        except ImportError:
            # Fallback if psutil not available
            return {
                "os": platform.system(),
                "cpu_count": os.cpu_count(),
                "python_version": platform.python_version(),
                "note": "Limited info - psutil not available"
            }