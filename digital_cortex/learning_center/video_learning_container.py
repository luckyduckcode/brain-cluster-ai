"""
Video Learning Container

Container for video processing capabilities in Chappy's Digital Body.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .video_learning_orchestrator import VideoLearningOrchestrator
from .knowledge_retrieval import KnowledgeRetrievalSystem
from ..utils.message import Message


class VideoLearningContainer:
    """
    Container that manages video learning capabilities
    """

    def __init__(self, corpus_colosseum=None, memory_palace=None):
        self.orchestrator = VideoLearningOrchestrator(corpus_colosseum, memory_palace)
        self.knowledge_retrieval = KnowledgeRetrievalSystem(memory_palace, corpus_colosseum)

        # Container state
        self.is_active = False
        self.current_learning_session = None

        # Learning history
        self.learning_history = []

    async def initialize(self) -> bool:
        """Initialize the video learning container"""
        try:
            self.is_active = True
            print("🎥 Video Learning Container initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Video Learning Container: {e}")
            return False

    async def shutdown(self):
        """Shutdown the container"""
        self.is_active = False
        print("🎥 Video Learning Container shut down")

    async def process_message(self, message: Message) -> Optional[Message]:
        """
        Process incoming messages related to video learning

        Args:
            message: Incoming message

        Returns:
            Response message or None
        """
        if not self.is_active:
            return None

        content = message.content.lower()

        # Handle video learning commands
        if content.startswith("learn from video:") or content.startswith("watch video:"):
            video_url = content.split(":", 1)[1].strip()
            return await self._handle_video_learning(video_url, message)

        elif content.startswith("what do you know about") or content.startswith("recall"):
            query = content.replace("what do you know about", "").replace("recall", "").strip()
            return await self._handle_knowledge_query(query, message)

        elif content == "learning stats" or content == "show learning statistics":
            return await self._handle_learning_stats(message)

        elif content.startswith("find videos about"):
            topic = content.replace("find videos about", "").strip()
            return await self._handle_find_videos(topic, message)

        return None

    async def _handle_video_learning(self, video_url: str, original_message: Message) -> Message:
        """Handle video learning request"""
        try:
            # Start learning session
            self.current_learning_session = {
                'start_time': datetime.now(),
                'video_url': video_url,
                'requester': original_message.source
            }

            # Progress callback for real-time updates
            progress_updates = []

            def progress_callback(update: str):
                progress_updates.append(update)
                print(f"📺 {update}")

            # Learn from video
            learning_results = await self.orchestrator.learn_from_video(
                video_url, progress_callback
            )

            # End session
            self.current_learning_session['end_time'] = datetime.now()
            self.current_learning_session['results'] = learning_results
            self.learning_history.append(self.current_learning_session.copy())
            self.current_learning_session = None

            # Create response
            if learning_results.get('success', False):
                response_content = f"""✅ Successfully learned from video!

📊 Learning Results:
• Processing Time: {learning_results.get('total_time', 0):.1f} seconds
• Knowledge Extracted: {len(learning_results.get('stages', {}).get('knowledge', {}).get('structured_knowledge', {}))} items
• Confidence: {learning_results.get('stages', {}).get('consensus', {}).get('confidence', 0.5):.2f}

🎯 Key Learnings:
{self._format_learning_summary(learning_results)}"""
            else:
                error_msg = learning_results.get('error', 'Unknown error')
                response_content = f"❌ Failed to learn from video: {error_msg}"

            return Message.create(
                source="video_learning_container",
                content=response_content,
                confidence=0.9 if learning_results.get('success') else 0.1,
                metadata={
                    'learning_results': learning_results,
                    'progress_updates': progress_updates
                }
            )

        except Exception as e:
            return Message.create(
                source="video_learning_container",
                content=f"❌ Error processing video learning request: {str(e)}",
                confidence=0.1
            )

    async def _handle_knowledge_query(self, query: str, original_message: Message) -> Message:
        """Handle knowledge retrieval query"""
        try:
            knowledge_result = await self.knowledge_retrieval.retrieve_knowledge(query)

            if knowledge_result.get('found_knowledge', False):
                response_content = f"""📚 Based on my video learning:

{knowledge_result.get('response', '')}

🎯 Confidence: {knowledge_result.get('confidence', 0.5):.2f}
📖 Sources: {len(knowledge_result.get('sources', []))} video(s)"""
            else:
                response_content = knowledge_result.get('response', 'No knowledge found for this query.')

            return Message.create(
                source="video_learning_container",
                content=response_content,
                confidence=knowledge_result.get('confidence', 0.5),
                metadata={'knowledge_query': query, 'result': knowledge_result}
            )

        except Exception as e:
            return Message.create(
                source="video_learning_container",
                content=f"❌ Error retrieving knowledge: {str(e)}",
                confidence=0.1
            )

    async def _handle_learning_stats(self, original_message: Message) -> Message:
        """Handle learning statistics request"""
        try:
            orchestrator_stats = self.orchestrator.get_learning_stats()
            retrieval_summary = await self.knowledge_retrieval.get_learning_summary()

            response_content = f"""📊 Video Learning Statistics:

🎥 Videos Processed: {orchestrator_stats.get('videos_processed', 0)}
⏱️ Total Learning Time: {orchestrator_stats.get('total_learning_time', 0):.1f} seconds
🎯 Average Confidence: {orchestrator_stats.get('average_confidence', 0.0):.2f}
📚 Knowledge Items Extracted: {orchestrator_stats.get('knowledge_extracted', 0)}

🧠 Knowledge Base Summary:
• Total Videos: {retrieval_summary.get('total_videos', 0)}
• Topics Covered: {', '.join(retrieval_summary.get('topics', []))}
• Knowledge Items: {retrieval_summary.get('total_knowledge_items', 0)}

📈 Recent Sessions: {len(self.learning_history)} completed"""

            return Message.create(
                source="video_learning_container",
                content=response_content,
                confidence=0.95
            )

        except Exception as e:
            return Message(
                source="video_learning_container",
                content=f"❌ Error retrieving statistics: {str(e)}",
                confidence=0.1
            )

    async def _handle_find_videos(self, topic: str, original_message: Message) -> Message:
        """Handle request to find videos about a topic"""
        try:
            related_videos = await self.knowledge_retrieval.find_related_videos(topic)

            if related_videos:
                video_list = "\n".join([
                    f"• {video['title']} (Relevance: {video['relevance_score']:.2f})"
                    for video in related_videos
                ])
                response_content = f"🎥 Videos I know about '{topic}':\n{video_list}"
            else:
                response_content = f"📭 I haven't learned about '{topic}' from any videos yet."

            return Message.create(
                source="video_learning_container",
                content=response_content,
                confidence=0.8
            )

        except Exception as e:
            return Message.create(
                source="video_learning_container",
                content=f"❌ Error finding videos: {str(e)}",
                confidence=0.1
            )

    def _format_learning_summary(self, learning_results: Dict[str, Any]) -> str:
        """Format learning results for display"""
        knowledge = learning_results.get('stages', {}).get('knowledge', {}).get('structured_knowledge', {})

        if not knowledge:
            return "No structured knowledge extracted."

        summary_parts = []

        if 'topic' in knowledge:
            summary_parts.append(f"Topic: {knowledge['topic']}")

        if 'key_takeaways' in knowledge and knowledge['key_takeaways']:
            takeaways = knowledge['key_takeaways'][:3]  # Show top 3
            summary_parts.append(f"Key Takeaways: {'; '.join(takeaways)}")

        if 'facts' in knowledge and knowledge['facts']:
            facts = knowledge['facts'][:2]  # Show top 2
            summary_parts.append(f"Facts: {'; '.join(facts)}")

        return "\n".join(f"• {part}" for part in summary_parts)

    def get_container_info(self) -> Dict[str, Any]:
        """Get container information"""
        return {
            'name': 'Video Learning Container',
            'type': 'learning',
            'capabilities': [
                'video_processing',
                'multimodal_learning',
                'knowledge_retrieval',
                'youtube_integration'
            ],
            'status': 'active' if self.is_active else 'inactive',
            'learning_sessions': len(self.learning_history),
            'current_session': self.current_learning_session is not None
        }