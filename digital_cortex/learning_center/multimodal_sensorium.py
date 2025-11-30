"""
Multimodal Sensorium for Video Learning

Processes visual, audio, and text information from videos using specialized models.
"""

import asyncio
import base64
import json
import time
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
import requests
from datetime import datetime

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class VisionSensorium:
    """
    Processes visual information from video frames using vision-language models
    """

    def __init__(self, model_name: str = "llava:7b", ollama_host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_host = ollama_host
        self.processing_queue = asyncio.Queue(maxsize=10)

    async def process_frame(self, frame: np.ndarray, timestamp: float) -> Dict[str, Any]:
        """
        Analyze a single frame using vision LLM

        Args:
            frame: OpenCV image array
            timestamp: Frame timestamp in seconds

        Returns:
            Dict with frame analysis
        """
        # Convert frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        prompt = """Describe what you see in this video frame in detail. Focus on:
1. Main objects and people visible
2. Actions or activities happening
3. Text or writing on screen
4. Setting/environment
5. Any important visual details

Be specific and descriptive."""

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "images": [img_base64],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent descriptions
                        "num_predict": 200
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'type': 'vision_frame',
                    'timestamp': timestamp,
                    'content': result.get('response', ''),
                    'confidence': 0.8,
                    'source': 'VisionSensorium',
                    'frame_shape': frame.shape,
                    'model_used': self.model_name
                }
            else:
                return {
                    'type': 'vision_frame',
                    'timestamp': timestamp,
                    'content': f"Vision processing failed: {response.status_code}",
                    'confidence': 0.0,
                    'source': 'VisionSensorium',
                    'error': True
                }

        except Exception as e:
            return {
                'type': 'vision_frame',
                'timestamp': timestamp,
                'content': f"Vision processing error: {str(e)}",
                'confidence': 0.0,
                'source': 'VisionSensorium',
                'error': True
            }

    async def process_video_sequence(self, frames: List[np.ndarray],
                                   timestamps: List[float]) -> Dict[str, Any]:
        """
        Process multiple frames and understand temporal relationships

        Args:
            frames: List of OpenCV image arrays
            timestamps: Corresponding timestamps

        Returns:
            Dict with sequence analysis
        """
        if not frames:
            return {'type': 'vision_sequence', 'frames': [], 'summary': 'No frames to process'}

        # Process frames in parallel with concurrency limit
        semaphore = asyncio.Semaphore(3)  # Limit concurrent vision API calls

        async def process_with_limit(frame, ts):
            async with semaphore:
                return await self.process_frame(frame, ts)

        # Process all frames
        tasks = [process_with_limit(frame, ts) for frame, ts in zip(frames, timestamps)]
        frame_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and get valid results
        valid_results = [r for r in frame_results if isinstance(r, dict) and not r.get('error', False)]

        if not valid_results:
            return {
                'type': 'vision_sequence',
                'frames': [],
                'summary': 'No frames could be processed successfully'
            }

        # Synthesize temporal understanding
        sequence_summary = await self._synthesize_sequence(valid_results)

        return {
            'type': 'vision_sequence',
            'frames': valid_results,
            'summary': sequence_summary,
            'frame_count': len(valid_results),
            'duration': timestamps[-1] - timestamps[0] if timestamps else 0
        }

    async def _synthesize_sequence(self, frame_descriptions: List[Dict[str, Any]]) -> str:
        """
        Use LLM to understand the sequence of frames and create a coherent summary
        """
        if len(frame_descriptions) <= 1:
            return frame_descriptions[0]['content'] if frame_descriptions else "No frames to analyze"

        # Create a condensed version of frame descriptions
        frames_text = "\n".join([
            f"Frame {i+1} ({fd['timestamp']:.1f}s): {fd['content'][:100]}{'...' if len(fd['content']) > 100 else ''}"
            for i, fd in enumerate(frame_descriptions[:10])  # Limit to first 10 frames
        ])

        if len(frame_descriptions) > 10:
            frames_text += f"\n... and {len(frame_descriptions) - 10} more frames"

        prompt = f"""Analyze this sequence of video frames and provide a coherent summary of what happens in this video segment:

{frames_text}

Focus on:
1. The main activity or process shown
2. How it develops over time
3. Key events or changes
4. Overall purpose or demonstration

Provide a concise but comprehensive summary."""

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2:1b",  # Use text-only model for synthesis
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 300
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json().get('response', 'Synthesis failed')
            else:
                return f"Failed to synthesize sequence: {response.status_code}"

        except Exception as e:
            return f"Sequence synthesis error: {str(e)}"


class AudioSensorium:
    """
    Processes audio/speech from videos using Whisper
    """

    def __init__(self, model_size: str = "base", device: str = "cpu"):
        self.model_size = model_size
        self.device = device
        self.model = None

    async def initialize_model(self):
        """Initialize Whisper model"""
        if not WHISPER_AVAILABLE:
            raise ImportError("whisper is required. Install with: pip install openai-whisper")

        if self.model is None:
            import whisper
            self.model = whisper.load_model(self.model_size, device=self.device)

    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Convert speech to text using Whisper

        Args:
            audio_path: Path to audio file

        Returns:
            Dict with transcription results
        """
        await self.initialize_model()

        if not os.path.exists(audio_path):
            return {
                'type': 'audio',
                'transcript': '',
                'segments': [],
                'error': f"Audio file not found: {audio_path}"
            }

        try:
            result = self.model.transcribe(
                audio_path,
                language='en',  # Assume English for now
                task='transcribe',
                verbose=False
            )

            return {
                'type': 'audio',
                'transcript': result.get('text', ''),
                'segments': result.get('segments', []),
                'language': result.get('language', 'en'),
                'confidence': 0.85,  # Whisper doesn't provide per-segment confidence easily
                'source': 'AudioSensorium',
                'duration': result.get('duration', 0)
            }

        except Exception as e:
            return {
                'type': 'audio',
                'transcript': '',
                'segments': [],
                'error': f"Audio transcription failed: {str(e)}"
            }

    async def extract_concepts_from_speech(self, transcript: str) -> Dict[str, Any]:
        """
        Use LLM to extract key concepts and knowledge from transcript
        """
        if not transcript.strip():
            return {'concepts': [], 'error': 'Empty transcript'}

        prompt = f"""Analyze this video transcript and extract structured knowledge:

{transcript}

Extract and categorize:
1. FACTS: Concrete information stated
2. CONCEPTS: Abstract ideas or principles explained
3. PROCEDURES: Step-by-step processes or instructions
4. EXAMPLES: Specific demonstrations or use cases
5. KEY POINTS: Important takeaways or conclusions

Format as JSON with these categories as keys."""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                try:
                    # Try to parse as JSON
                    knowledge = json.loads(result.get('response', '{}'))
                    return knowledge
                except json.JSONDecodeError:
                    # Fallback to text response
                    return {'extracted_knowledge': result.get('response', '')}
            else:
                return {'error': f'API call failed: {response.status_code}'}

        except Exception as e:
            return {'error': f'Knowledge extraction failed: {str(e)}'}


class TextSensorium:
    """
    Processes text from captions, OCR, and video descriptions
    """

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host

    async def process_captions(self, captions_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process subtitle/caption files
        """
        if not captions_data:
            return {
                'type': 'text',
                'content': '',
                'source': 'TextSensorium',
                'confidence': 0.0
            }

        # Extract English captions if available
        captions_text = ""
        if 'en' in captions_data:
            en_captions = captions_data['en']
            if isinstance(en_captions, list):
                captions_text = ' '.join([cap.get('text', '') for cap in en_captions])
            elif isinstance(en_captions, str):
                captions_text = en_captions

        return {
            'type': 'text',
            'content': captions_text,
            'source': 'TextSensorium',
            'confidence': 0.9 if captions_text else 0.0,
            'language': 'en'
        }

    async def extract_video_description_knowledge(self, description: str) -> Dict[str, Any]:
        """
        Extract knowledge from video description
        """
        if not description.strip():
            return {'description_knowledge': {}}

        prompt = f"""Analyze this YouTube video description and extract:

{description}

Extract:
1. TOPIC: Main subject matter
2. LEARNING_OBJECTIVES: What viewers will learn
3. PREREQUISITES: Required background knowledge
4. RESOURCES: Links or additional materials mentioned
5. KEY_CONCEPTS: Important terms or ideas

Format as structured information."""

        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=30
            )

            if response.status_code == 200:
                return {
                    'description_analysis': response.json().get('response', ''),
                    'raw_description': description
                }
            else:
                return {'error': f'Description analysis failed: {response.status_code}'}

        except Exception as e:
            return {'error': f'Description analysis error: {str(e)}'}