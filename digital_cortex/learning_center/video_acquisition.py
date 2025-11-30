"""
Chappy's YouTube Learning System

Complete integration architecture for video-based learning with multimodal processing.
"""

import os
import asyncio
import tempfile
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
import requests
import base64
from io import BytesIO
from PIL import Image

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class VideoAcquisitionSystem:
    """
    Fetches and preprocesses YouTube videos for learning
    """

    def __init__(self, download_path: str = "/tmp/chappy_videos"):
        self.download_path = download_path
        os.makedirs(download_path, exist_ok=True)

    async def fetch_video(self, youtube_url: str) -> Dict[str, Any]:
        """
        Download video and extract components

        Returns: {
            'video_path': str,
            'audio_path': str,
            'metadata': dict,
            'duration': float,
            'frames': List[np.ndarray]
        }
        """
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is required for video downloading. Install with: pip install yt-dlp")

        # Create temporary directory for this video
        video_id = self._extract_video_id(youtube_url)
        video_dir = os.path.join(self.download_path, video_id)
        os.makedirs(video_dir, exist_ok=True)

        # yt-dlp options for downloading
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': os.path.join(video_dir, '%(id)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)

            video_path = os.path.join(video_dir, f"{info['id']}.mp4")
            audio_path = os.path.join(video_dir, f"{info['id']}.m4a")

            # If audio wasn't extracted separately, use the video file
            if not os.path.exists(audio_path):
                audio_path = video_path

            # Extract frames at 1 FPS for processing
            frames = await self.extract_frames(video_path, fps=1.0)

            return {
                'video_path': video_path,
                'audio_path': audio_path,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'description': info.get('description', ''),
                'uploader': info.get('uploader', ''),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
                'captions': info.get('subtitles', {}),
                'frames': frames,
                'frame_count': len(frames),
                'video_id': video_id,
                'url': youtube_url
            }

        except Exception as e:
            raise Exception(f"Failed to download video: {e}")

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Fallback: use URL hash
        return str(hash(url))[-10:]

    async def extract_frames(self, video_path: str, fps: float = 1.0) -> List[np.ndarray]:
        """
        Extract frames at specified rate

        Args:
            video_path: Path to video file
            fps: Frames per second to extract

        Returns:
            List of numpy arrays (frames)
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")

        frames = []
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(original_fps / fps) if fps > 0 else 1

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frames.append(frame)

            frame_count += 1

        cap.release()
        return frames

    async def get_video_metadata(self, youtube_url: str) -> Dict[str, Any]:
        """
        Get video metadata without downloading
        """
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is required")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

        return {
            'title': info.get('title', ''),
            'duration': info.get('duration', 0),
            'description': info.get('description', ''),
            'uploader': info.get('uploader', ''),
            'view_count': info.get('view_count', 0),
            'upload_date': info.get('upload_date', ''),
            'thumbnail': info.get('thumbnail', ''),
        }