"""
Knowledge Retrieval System

Retrieves and synthesizes learned knowledge from videos for Chappy's responses.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests

from ..utils.message import Message


class KnowledgeRetrievalSystem:
    """
    Retrieves and synthesizes knowledge from learned videos
    """

    def __init__(self, memory_palace=None, corpus_colosseum=None):
        self.memory_palace = memory_palace
        self.corpus_colosseum = corpus_colosseum

        # Cache for recent queries
        self.query_cache = {}
        self.cache_expiry = 300  # 5 minutes

    async def retrieve_knowledge(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge from learned videos

        Args:
            query: Natural language query about learned content
            context: Optional context (conversation history, current topic, etc.)

        Returns:
            Dict with retrieved knowledge and synthesis
        """
        # Check cache first
        context_str = json.dumps(context, sort_keys=True) if context else 'no_context'
        cache_key = f"{query}_{hash(context_str)}"
        if cache_key in self.query_cache:
            cached_result, timestamp = self.query_cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_expiry:
                return cached_result

        try:
            # Step 1: Search memory palace for relevant video knowledge
            relevant_memories = await self._search_video_memories(query)

            if not relevant_memories:
                return {
                    'query': query,
                    'found_knowledge': False,
                    'response': "I haven't learned about this topic from videos yet.",
                    'confidence': 0.0
                }

            # Step 2: Synthesize knowledge from multiple sources
            synthesized_knowledge = await self._synthesize_retrieved_knowledge(
                query, relevant_memories, context
            )

            # Step 3: Create response through consensus if available
            if self.corpus_colosseum:
                final_response = await self._achieve_response_consensus(
                    synthesized_knowledge, query
                )
            else:
                final_response = synthesized_knowledge.get('synthesized_response', '')

            result = {
                'query': query,
                'found_knowledge': True,
                'response': final_response,
                'confidence': synthesized_knowledge.get('confidence', 0.5),
                'sources': synthesized_knowledge.get('sources', []),
                'knowledge_type': 'video_learning'
            }

            # Cache result
            self.query_cache[cache_key] = (result, datetime.now())

            return result

        except Exception as e:
            return {
                'query': query,
                'found_knowledge': False,
                'response': f"Error retrieving knowledge: {str(e)}",
                'confidence': 0.0
            }

    async def _search_video_memories(self, query: str) -> List[Dict[str, Any]]:
        """Search memory palace for video-related knowledge"""
        if not self.memory_palace:
            return []

        # This would use the memory palace's search capabilities
        # For now, we'll simulate by returning mock data
        # In a real implementation, this would query the memory palace

        # Mock search results - replace with actual memory palace search
        mock_memories = [
            {
                'memory_address': 'video_001',
                'content': {
                    'type': 'video_learning',
                    'source_title': 'Introduction to Machine Learning',
                    'knowledge': {
                        'topic': 'Machine Learning',
                        'facts': ['ML uses algorithms to learn from data', 'Supervised learning requires labeled data'],
                        'concepts': ['Training data', 'Model accuracy', 'Overfitting'],
                        'key_takeaways': ['ML can predict outcomes from data patterns']
                    },
                    'learning_confidence': 0.85
                },
                'relevance_score': 0.9
            }
        ]

        return mock_memories

    async def _synthesize_retrieved_knowledge(self, query: str,
                                            memories: List[Dict[str, Any]],
                                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesize knowledge from multiple video sources"""

        # Combine all relevant knowledge
        combined_knowledge = {
            'topics': [],
            'facts': [],
            'concepts': [],
            'procedures': [],
            'examples': [],
            'key_takeaways': [],
            'sources': []
        }

        for memory in memories:
            content = memory.get('content', {})
            knowledge = content.get('knowledge', {})

            # Aggregate knowledge from each source
            for key in combined_knowledge.keys():
                if key in knowledge:
                    if isinstance(knowledge[key], list):
                        combined_knowledge[key].extend(knowledge[key])
                    else:
                        combined_knowledge[key].append(knowledge[key])

            # Track sources
            combined_knowledge['sources'].append({
                'title': content.get('source_title', 'Unknown Video'),
                'url': content.get('source_url', ''),
                'confidence': content.get('learning_confidence', 0.5),
                'relevance': memory.get('relevance_score', 0.5)
            })

        # Remove duplicates while preserving order
        for key in combined_knowledge:
            if isinstance(combined_knowledge[key], list):
                # Handle different types of items
                seen = set()
                unique_items = []
                for item in combined_knowledge[key]:
                    # Convert to string for hashing if it's a dict
                    item_key = json.dumps(item, sort_keys=True) if isinstance(item, dict) else item
                    if item_key not in seen:
                        seen.add(item_key)
                        unique_items.append(item)
                combined_knowledge[key] = unique_items

        # Use LLM to synthesize coherent response
        synthesis_prompt = f"""Based on the following knowledge retrieved from videos, answer this query: "{query}"

RETRIEVED KNOWLEDGE:
Topics: {', '.join(combined_knowledge['topics'])}
Facts: {'; '.join(combined_knowledge['facts'])}
Concepts: {', '.join(combined_knowledge['concepts'])}
Key Takeaways: {'; '.join(combined_knowledge['key_takeaways'])}

Sources: {len(combined_knowledge['sources'])} video(s)

Provide a comprehensive but concise answer based on this knowledge. If the query cannot be fully answered with the available knowledge, note what information is missing."""

        if context:
            synthesis_prompt += f"\n\nAdditional Context: {json.dumps(context)}"

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": synthesis_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                synthesized_response = result.get('response', '').strip()
                confidence = 0.8 if synthesized_response else 0.3
            else:
                synthesized_response = "Unable to synthesize response from video knowledge."
                confidence = 0.2

        except Exception as e:
            synthesized_response = f"Error synthesizing knowledge: {str(e)}"
            confidence = 0.1

        return {
            'synthesized_response': synthesized_response,
            'confidence': confidence,
            'sources': combined_knowledge['sources'],
            'knowledge_summary': combined_knowledge
        }

    async def _achieve_response_consensus(self, synthesized_knowledge: Dict[str, Any],
                                        original_query: str) -> str:
        """Use corpus colosseum to achieve consensus on the response"""
        if not self.corpus_colosseum:
            return synthesized_knowledge.get('synthesized_response', '')

        # Create messages from different perspectives
        messages = [
            Message.create(
                source="knowledge_synthesis",
                content=synthesized_knowledge.get('synthesized_response', ''),
                confidence=synthesized_knowledge.get('confidence', 0.5)
            )
        ]

        # Add source-specific messages for consensus
        for source in synthesized_knowledge.get('sources', []):
            messages.append(Message.create(
                source=f"video_{source.get('title', 'unknown')}",
                content=f"From video '{source.get('title', 'unknown')}': {source}",
                confidence=source.get('confidence', 0.5)
            ))

        # Find consensus
        winner, metadata = self.corpus_colosseum.find_consensus(messages)

        if winner:
            return winner.content
        else:
            return synthesized_knowledge.get('synthesized_response', '')

    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of all learned video knowledge"""
        if not self.memory_palace:
            return {'total_videos': 0, 'topics': [], 'summary': 'No memory palace available'}

        # This would query the memory palace for all video learning memories
        # For now, return mock summary
        return {
            'total_videos': 5,
            'topics': ['Machine Learning', 'Neural Networks', 'Data Science', 'AI Ethics'],
            'total_knowledge_items': 47,
            'average_confidence': 0.78,
            'last_learning_session': datetime.now().isoformat()
        }

    async def find_related_videos(self, topic: str) -> List[Dict[str, Any]]:
        """Find videos related to a specific topic"""
        # This would search through stored video metadata
        # For now, return mock results
        return [
            {
                'title': f'Introduction to {topic}',
                'url': f'https://youtube.com/watch?v=mock_{topic.lower().replace(" ", "_")}',
                'relevance_score': 0.9,
                'learned_date': datetime.now().isoformat()
            }
        ]

    def clear_cache(self):
        """Clear the query cache"""
        self.query_cache.clear()