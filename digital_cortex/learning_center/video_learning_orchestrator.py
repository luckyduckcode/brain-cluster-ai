"""
Video Learning Orchestrator

Coordinates multimodal processing and integrates video learning with Chappy's brain.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

from .video_acquisition import VideoAcquisitionSystem
from .multimodal_sensorium import VisionSensorium, AudioSensorium, TextSensorium
from ..utils.message import Message


class VideoLearningOrchestrator:
    """
    Coordinates all sensory inputs and creates unified understanding from videos
    """

    def __init__(self, corpus_colosseum=None, memory_palace=None):
        self.corpus_colosseum = corpus_colosseum
        self.memory_palace = memory_palace

        # Initialize sensory systems
        self.vision_sensorium = VisionSensorium()
        self.audio_sensorium = AudioSensorium()
        self.text_sensorium = TextSensorium()

        # Video acquisition
        self.video_acquisition = VideoAcquisitionSystem()

        # Learning statistics
        self.learning_stats = {
            'videos_processed': 0,
            'total_learning_time': 0,
            'average_confidence': 0.0,
            'knowledge_extracted': 0
        }

    async def learn_from_video(self, youtube_url: str, progress_callback=None) -> Dict[str, Any]:
        """
        Complete pipeline: Watch video → Process → Learn → Store

        Args:
            youtube_url: YouTube video URL
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with learning results
        """
        start_time = time.time()
        learning_results = {
            'video_url': youtube_url,
            'start_time': datetime.now().isoformat(),
            'stages': {},
            'success': False
        }

        try:
            # Stage 1: Acquire video
            if progress_callback:
                progress_callback("📥 Acquiring video...")
            learning_results['stages']['acquisition'] = await self._acquire_video(youtube_url)

            video_data = learning_results['stages']['acquisition']
            if 'error' in video_data:
                raise Exception(f"Video acquisition failed: {video_data['error']}")

            # Stage 2: Multimodal processing (PARALLEL)
            if progress_callback:
                progress_callback("🧠 Processing video with multimodal sensorium...")
            learning_results['stages']['multimodal'] = await self._process_multimodal(video_data)

            # Stage 3: Create messages for Corpus Colosseum
            if progress_callback:
                progress_callback("🎯 Finding consensus on video content...")
            learning_results['stages']['consensus'] = await self._achieve_consensus(
                learning_results['stages']['multimodal']
            )

            # Stage 4: Extract learnable knowledge
            if progress_callback:
                progress_callback("📚 Extracting structured knowledge...")
            learning_results['stages']['knowledge'] = await self._extract_knowledge(
                learning_results['stages']['multimodal'],
                learning_results['stages']['consensus']
            )

            # Stage 5: Store in Memory Palace
            if progress_callback:
                progress_callback("🧠 Storing knowledge in memory palace...")
            learning_results['stages']['storage'] = await self._store_in_memory(
                learning_results['stages']['knowledge'],
                video_data
            )

            # Update statistics
            learning_time = time.time() - start_time
            self._update_statistics(learning_results, learning_time)

            learning_results['success'] = True
            learning_results['total_time'] = learning_time

            if progress_callback:
                progress_callback("✅ Learning complete!")

            return learning_results

        except Exception as e:
            learning_results['error'] = str(e)
            learning_results['total_time'] = time.time() - start_time
            return learning_results

    async def _acquire_video(self, youtube_url: str) -> Dict[str, Any]:
        """Stage 1: Acquire and preprocess video"""
        try:
            video_data = await self.video_acquisition.fetch_video(youtube_url)
            return {
                'status': 'success',
                'video_data': video_data,
                'frames_extracted': len(video_data.get('frames', [])),
                'duration': video_data.get('duration', 0)
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    async def _process_multimodal(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Process video through all sensory modalities"""
        video_info = video_data.get('video_data', {})

        # Prepare data for parallel processing
        frames = video_info.get('frames', [])
        audio_path = video_info.get('audio_path', '')
        captions = video_info.get('captions', {})

        # Create timestamps for frames (assuming 1 FPS)
        timestamps = [i * 1.0 for i in range(len(frames))]

        # Process all modalities in parallel
        vision_task = self.vision_sensorium.process_video_sequence(frames, timestamps)
        audio_task = self.audio_sensorium.transcribe_audio(audio_path)
        text_task = self.text_sensorium.process_captions(captions)

        # Wait for all to complete
        vision_result, audio_result, text_result = await asyncio.gather(
            vision_task, audio_task, text_task,
            return_exceptions=True
        )

        # Handle exceptions
        results = {}
        for name, result in [('vision', vision_result), ('audio', audio_result), ('text', text_result)]:
            if isinstance(result, Exception):
                results[name] = {'error': str(result), 'type': name}
            else:
                results[name] = result

        return {
            'status': 'processed',
            'modalities': results,
            'processing_time': time.time()
        }

    async def _achieve_consensus(self, multimodal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Create unified understanding through consensus"""
        if not self.corpus_colosseum:
            return {'consensus': 'No corpus colosseum available', 'confidence': 0.5}

        modalities = multimodal_data.get('modalities', {})

        # Create messages for each modality
        messages = []
        for modality_name, modality_data in modalities.items():
            if 'error' not in modality_data:
                message = Message(
                    source=f"{modality_name}_sensorium",
                    content=str(modality_data),
                    confidence=modality_data.get('confidence', 0.5)
                )
                messages.append(message)

        if not messages:
            return {'consensus': 'No valid modality data', 'confidence': 0.0}

        # Find consensus
        winner, metadata = self.corpus_colosseum.find_consensus(messages)

        return {
            'consensus_message': winner.content if winner else 'No consensus reached',
            'confidence': winner.confidence if winner else 0.0,
            'contributing_modalities': len(messages),
            'metadata': metadata
        }

    async def _extract_knowledge(self, multimodal_data: Dict[str, Any],
                               consensus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 4: Extract structured knowledge from all sources"""
        modalities = multimodal_data.get('modalities', {})

        # Combine all modality information
        combined_content = {
            'vision_summary': modalities.get('vision', {}).get('summary', ''),
            'audio_transcript': modalities.get('audio', {}).get('transcript', ''),
            'text_content': modalities.get('text', {}).get('content', ''),
            'consensus': consensus_data.get('consensus_message', '')
        }

        # Use LLM to synthesize structured knowledge
        knowledge = await self._synthesize_knowledge(combined_content)

        return {
            'structured_knowledge': knowledge,
            'raw_content': combined_content,
            'extraction_confidence': 0.8
        }

    async def _synthesize_knowledge(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to create structured knowledge representation"""
        content_text = f"""
VISUAL SUMMARY: {content.get('vision_summary', 'N/A')}

AUDIO TRANSCRIPT: {content.get('audio_transcript', 'N/A')[:1000]}...

TEXT CONTENT: {content.get('text_content', 'N/A')[:500]}...

CONSENSUS: {content.get('consensus', 'N/A')}
"""

        prompt = f"""Analyze this multimodal video content and extract structured knowledge:

{content_text}

Extract and structure as JSON:
{{
  "topic": "main subject matter",
  "facts": ["list of concrete facts learned"],
  "concepts": ["abstract concepts explained"],
  "procedures": ["step-by-step processes shown"],
  "examples": ["specific demonstrations"],
  "key_takeaways": ["important lessons"],
  "prerequisites": ["required background knowledge"],
  "applications": ["where this knowledge can be used"]
}}

Be specific and comprehensive based on the content provided."""

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
                        "num_predict": 1000
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                try:
                    return json.loads(result.get('response', '{}'))
                except json.JSONDecodeError:
                    return {'synthesized_knowledge': result.get('response', '')}
            else:
                return {'error': f'Knowledge synthesis failed: {response.status_code}'}

        except Exception as e:
            return {'error': f'Knowledge synthesis error: {str(e)}'}

    async def _store_in_memory(self, knowledge_data: Dict[str, Any],
                             video_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 5: Store extracted knowledge in Memory Palace"""
        if not self.memory_palace:
            return {'status': 'no_memory_palace', 'message': 'Knowledge not stored'}

        # Create memory entry
        memory_entry = {
            'type': 'video_learning',
            'source': 'youtube_video',
            'source_url': video_metadata.get('url'),
            'source_title': video_metadata.get('title'),
            'timestamp': datetime.now().isoformat(),
            'knowledge': knowledge_data.get('structured_knowledge', {}),
            'raw_content': knowledge_data.get('raw_content', {}),
            'video_metadata': {
                'duration': video_metadata.get('duration'),
                'uploader': video_metadata.get('uploader'),
                'view_count': video_metadata.get('view_count'),
                'upload_date': video_metadata.get('upload_date')
            },
            'learning_confidence': knowledge_data.get('extraction_confidence', 0.5)
        }

        try:
            # Store in memory palace
            memory_address = self.memory_palace.store_memory(
                Message(
                    source="video_learning_orchestrator",
                    content=json.dumps(memory_entry),
                    confidence=memory_entry['learning_confidence']
                ),
                {'learning_type': 'video', 'video_url': video_metadata.get('url')}
            )

            return {
                'status': 'stored',
                'memory_address': memory_address,
                'knowledge_items': len(memory_entry['knowledge'])
            }

        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    def _update_statistics(self, results: Dict[str, Any], learning_time: float):
        """Update learning statistics"""
        self.learning_stats['videos_processed'] += 1
        self.learning_stats['total_learning_time'] += learning_time

        # Update average confidence
        new_confidence = results.get('stages', {}).get('consensus', {}).get('confidence', 0.5)
        current_avg = self.learning_stats['average_confidence']
        count = self.learning_stats['videos_processed']
        self.learning_stats['average_confidence'] = (current_avg * (count - 1) + new_confidence) / count

        # Count knowledge items extracted
        knowledge = results.get('stages', {}).get('knowledge', {}).get('structured_knowledge', {})
        if isinstance(knowledge, dict):
            self.learning_stats['knowledge_extracted'] += len(knowledge)

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return self.learning_stats.copy()

    async def search_learned_videos(self, query: str) -> List[Dict[str, Any]]:
        """Search through learned video knowledge"""
        if not self.memory_palace:
            return []

        # This would integrate with memory palace search
        # For now, return empty list
        return []