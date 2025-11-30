"""
Enhanced RAG Memory System for Chappy AI

This module implements a Retrieval-Augmented Generation system using:
- ChromaDB for local vector storage
- SentenceTransformers for embeddings
- Integration with existing Chappy brain architecture
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    YouTubeTranscriptApi = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChappyRAGMemory:
    """
    RAG-based memory system for Chappy AI.

    Features:
    - Local vector database (ChromaDB)
    - Semantic search and retrieval
    - Conversation memory with context
    - Web search integration
    - Video content handling
    """

    def __init__(self, persist_directory: str = "./chappy_memory"):
        """
        Initialize the RAG memory system.

        Args:
            persist_directory: Directory to store the vector database
        """
        self.persist_directory = persist_directory
        self.embedding_model = None
        self.chroma_client = None
        self.conversation_collection = None
        self.knowledge_collection = None

        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_db()
        self._initialize_collections()

        logger.info("Chappy RAG Memory System initialized")

    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model for embeddings."""
        try:
            # Use a lightweight but effective model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

    def _initialize_vector_db(self):
        """Initialize ChromaDB client with persistence."""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _initialize_collections(self):
        """Initialize ChromaDB collections for different memory types."""
        try:
            # Collection for conversation history
            self.conversation_collection = self.chroma_client.get_or_create_collection(
                name="conversations",
                metadata={"description": "Chappy's conversation memory"}
            )

            # Collection for general knowledge and web content
            self.knowledge_collection = self.chroma_client.get_or_create_collection(
                name="knowledge",
                metadata={"description": "General knowledge and web content"}
            )

            logger.info("Memory collections initialized")
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise

    def store_conversation(self, user_message: str, chappy_response: str,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a conversation turn in the vector database.

        Args:
            user_message: The user's message
            chappy_response: Chappy's response
            metadata: Additional metadata

        Returns:
            ID of the stored conversation
        """
        try:
            # Create conversation text for embedding
            conversation_text = f"User: {user_message}\nChappy: {chappy_response}"

            # Generate embedding
            embedding = self.embedding_model.encode(conversation_text).tolist()

            # Create metadata
            conversation_metadata = {
                "type": "conversation",
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "user_message": user_message,
                "chappy_response": chappy_response
            }

            if metadata:
                conversation_metadata.update(metadata)

            # Generate unique ID
            conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

            # Store in ChromaDB
            self.conversation_collection.add(
                documents=[conversation_text],
                embeddings=[embedding],
                metadatas=[conversation_metadata],
                ids=[conversation_id]
            )

            logger.debug(f"Stored conversation: {conversation_id}")
            return conversation_id

        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            return ""

    def retrieve_relevant_memories(self, query: str, n_results: int = 5,
                                  memory_type: str = "conversation") -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on semantic similarity.

        Args:
            query: The search query
            n_results: Number of results to return
            memory_type: Type of memory to search ("conversation" or "knowledge")

        Returns:
            List of relevant memory documents with metadata
        """
        try:
            # Choose collection based on memory type
            collection = self.conversation_collection if memory_type == "conversation" else self.knowledge_collection

            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search for similar documents
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            # Format results
            memories = []
            if results['documents'] and results['metadatas']:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    memories.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance  # Convert distance to similarity
                    })

            logger.debug(f"Retrieved {len(memories)} relevant memories")
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []

    def store_knowledge(self, content: str, source: str = "unknown",
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store general knowledge or web content.

        Args:
            content: The knowledge content
            source: Source of the knowledge (e.g., "web_search", "video_transcript")
            metadata: Additional metadata

        Returns:
            ID of the stored knowledge
        """
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()

            # Create metadata
            knowledge_metadata = {
                "type": "knowledge",
                "source": source,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            if metadata:
                knowledge_metadata.update(metadata)

            # Generate unique ID
            knowledge_id = f"know_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

            # Store in ChromaDB
            self.knowledge_collection.add(
                documents=[content],
                embeddings=[embedding],
                metadatas=[knowledge_metadata],
                ids=[knowledge_id]
            )

            logger.debug(f"Stored knowledge: {knowledge_id}")
            return knowledge_id

        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            return ""

    def search_web_and_store(self, query: str, search_results: List[Dict[str, Any]]) -> int:
        """
        Store web search results in knowledge base.

        Args:
            query: The original search query
            search_results: List of search result dictionaries

        Returns:
            Number of results stored
        """
        stored_count = 0
        try:
            for result in search_results:
                # Create content from search result
                title = result.get('title', 'No title')
                url = result.get('url', '')
                snippet = result.get('snippet', result.get('body', ''))

                content = f"Title: {title}\nURL: {url}\nContent: {snippet}"

                # Store in knowledge base
                knowledge_id = self.store_knowledge(
                    content=content,
                    source="web_search",
                    metadata={
                        "query": query,
                        "title": title,
                        "url": url,
                        "search_engine": "duckduckgo"
                    }
                )

                if knowledge_id:
                    stored_count += 1

            logger.info(f"Stored {stored_count} web search results")
            return stored_count

        except Exception as e:
            logger.error(f"Failed to store web search results: {e}")
            return 0

    def get_memory_stats(self) -> Dict[str, int]:
        """
        Get statistics about stored memories.

        Returns:
            Dictionary with memory counts
        """
        try:
            conv_count = self.conversation_collection.count()
            know_count = self.knowledge_collection.count()

            return {
                "conversations": conv_count,
                "knowledge_items": know_count,
                "total_memories": conv_count + know_count
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}

    def clear_memory(self, memory_type: str = "all") -> bool:
        """
        Clear memories from the database.

        Args:
            memory_type: Type of memory to clear ("conversation", "knowledge", or "all")

        Returns:
            Success status
        """
        try:
            if memory_type in ["conversation", "all"]:
                self.chroma_client.delete_collection("conversations")
                self.conversation_collection = self.chroma_client.create_collection(
                    name="conversations",
                    metadata={"description": "Chappy's conversation memory"}
                )

            if memory_type in ["knowledge", "all"]:
                self.chroma_client.delete_collection("knowledge")
                self.knowledge_collection = self.chroma_client.create_collection(
                    name="knowledge",
                    metadata={"description": "General knowledge and web content"}
                )

            logger.info(f"Cleared {memory_type} memories")
            return True

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False


class WebSearchTool:
    """
    Simple web search tool for Chappy.
    """

    def __init__(self):
        """Initialize the web search tool."""
        try:
            from ddgs import DDGS
            self.search_engine = DDGS()
        except ImportError:
            logger.warning("ddgs not installed. Web search disabled.")
            self.search_engine = None

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a web search.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        if not self.search_engine:
            return []

        try:
            results = self.search_engine.text(query, max_results=max_results)
            return [
                {
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'snippet': result.get('body', '')
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []


class VideoUnderstandingTool:
    """
    Tool for understanding video content.
    """

    def __init__(self):
        """Initialize the video understanding tool."""
        self.transcript_api = None
        if YOUTUBE_TRANSCRIPT_AVAILABLE:
            self.transcript_api = YouTubeTranscriptApi
        else:
            logger.warning("youtube-transcript-api not installed. Video transcripts disabled.")

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.

        Args:
            url: YouTube URL

        Returns:
            Video ID or None
        """
        import re
        from urllib.parse import urlparse, parse_qs

        # YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Try parsing query parameters
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'youtu.be']:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]

        return None

    def get_video_transcript(self, url: str) -> Optional[str]:
        """
        Get transcript from YouTube video.

        Args:
            url: YouTube video URL

        Returns:
            Video transcript or None
        """
        if not self.transcript_api:
            return None

        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return None

            transcript = self.transcript_api.fetch(video_id)
            # Combine transcript pieces
            full_transcript = " ".join([entry['text'] for entry in transcript])
            return full_transcript

        except Exception as e:
            logger.error(f"Failed to get video transcript: {e}")
            return None

    def handle_video_request(self, url: str) -> str:
        """
        Handle a video-related request.

        Args:
            url: Video URL

        Returns:
            Response about the video
        """
        video_id = self.extract_video_id(url)

        if not video_id:
            return "I can't identify this as a valid YouTube URL. Could you double-check the link?"

        # Try to get transcript
        transcript = self.get_video_transcript(url)

        if transcript:
            # Store transcript in memory (would be called from main system)
            return f"I found a transcript for this video! It's about {len(transcript)} characters long. Would you like me to summarize it or answer specific questions about the content?"
        else:
            return "I can see this is a YouTube video, but I couldn't access the transcript. This might be because the video doesn't have captions enabled, or it's not a public video. What would you like to know about it instead?"