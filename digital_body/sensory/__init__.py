"""
Sensory System for Chappy's Digital Body

Handles all sensory inputs:
- Vision: Camera/webcam processing
- Audio: Microphone input and speech-to-text
- Text: Chat/API inputs
- System: Resource monitoring and system events
"""

import cv2
import numpy as np
import speech_recognition as sr
import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import queue
import json
import os

from ..message import BodyMessage


class SensorySystem:
    """Manages all sensory inputs for Chappy's body."""

    def __init__(self):
        self.vision_active = False
        self.audio_active = False
        self.system_active = False

        # Queues for different sensory inputs
        self.vision_queue = queue.Queue(maxsize=10)
        self.audio_queue = queue.Queue(maxsize=10)
        self.text_queue = queue.Queue(maxsize=10)
        self.system_queue = queue.Queue(maxsize=10)

        # Processing threads
        self.vision_thread = None
        self.audio_thread = None
        self.system_thread = None

        # Recognition objects
        self.recognizer = sr.Recognizer()
        self.microphone = None

        # System monitoring
        self.last_cpu_percent = 0
        self.last_memory_percent = 0

    def initialize_sensors(self) -> bool:
        """Initialize all available sensors."""
        try:
            # Initialize vision
            if self._init_vision():
                self.vision_active = True
                print("✅ Vision sensor initialized")

            # Initialize audio
            if self._init_audio():
                self.audio_active = True
                print("✅ Audio sensor initialized")

            # Initialize system monitoring
            self.system_active = True
            print("✅ System monitoring initialized")

            return True
        except Exception as e:
            print(f"❌ Failed to initialize sensors: {e}")
            return False

    def _init_vision(self) -> bool:
        """Initialize camera/vision sensor."""
        try:
            # Try to open default camera
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False

    def _init_audio(self) -> bool:
        """Initialize microphone/audio sensor."""
        try:
            self.microphone = sr.Microphone()
            # Test microphone
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            return True
        except:
            return False

    def start_sensory_processing(self):
        """Start all sensory processing threads."""
        if self.vision_active:
            self.vision_thread = threading.Thread(target=self._vision_loop, daemon=True)
            self.vision_thread.start()

        if self.audio_active:
            self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
            self.audio_thread.start()

        if self.system_active:
            self.system_thread = threading.Thread(target=self._system_loop, daemon=True)
            self.system_thread.start()

    def stop_sensory_processing(self):
        """Stop all sensory processing."""
        self.vision_active = False
        self.audio_active = False
        self.system_active = False

        # Wait for threads to finish
        if self.vision_thread and self.vision_thread.is_alive():
            self.vision_thread.join(timeout=1.0)
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
        if self.system_thread and self.system_thread.is_alive():
            self.system_thread.join(timeout=1.0)

    def _vision_loop(self):
        """Main vision processing loop."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return

        try:
            while self.vision_active:
                ret, frame = cap.read()
                if ret:
                    # Process frame (basic motion detection for now)
                    motion_detected = self._detect_motion(frame)

                    if motion_detected or self.vision_queue.empty():
                        # Create sensory message
                        message = BodyMessage.create_sensory(
                            sensor_type="vision",
                            data={
                                "frame_shape": frame.shape,
                                "motion_detected": motion_detected,
                                "timestamp": datetime.now().isoformat()
                            },
                            confidence=0.8
                        )
                        self._safe_put(self.vision_queue, message)

                time.sleep(0.1)  # 10 FPS

        except Exception as e:
            print(f"Vision processing error: {e}")
        finally:
            cap.release()

    def _detect_motion(self, frame) -> bool:
        """Simple motion detection."""
        # Convert to grayscale and blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Initialize background on first frame
        if not hasattr(self, '_background'):
            self._background = gray
            return False

        # Compute difference
        frame_delta = cv2.absdiff(self._background, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Update background occasionally
        self._background = cv2.addWeighted(self._background, 0.9, gray, 0.1, 0)

        # Check for significant motion
        motion_pixels = np.sum(thresh > 0)
        total_pixels = thresh.size
        motion_ratio = motion_pixels / total_pixels

        return motion_ratio > 0.01  # 1% motion threshold

    def _audio_loop(self):
        """Main audio processing loop."""
        try:
            while self.audio_active:
                if self.microphone:
                    with self.microphone as source:
                        try:
                            # Listen for audio
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                            # Convert to text
                            text = self.recognizer.recognize_google(audio)

                            if text.strip():
                                message = BodyMessage.create_sensory(
                                    sensor_type="audio",
                                    data={
                                        "text": text,
                                        "confidence": 0.9,
                                        "timestamp": datetime.now().isoformat()
                                    },
                                    confidence=0.9
                                )
                                self._safe_put(self.audio_queue, message)

                        except sr.WaitTimeoutError:
                            pass  # No speech detected
                        except sr.UnknownValueError:
                            pass  # Could not understand
                        except sr.RequestError as e:
                            print(f"Speech recognition error: {e}")

                time.sleep(0.1)

        except Exception as e:
            print(f"Audio processing error: {e}")

    def _system_loop(self):
        """Main system monitoring loop."""
        try:
            while self.system_active:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                # Check for significant changes
                cpu_change = abs(cpu_percent - self.last_cpu_percent)
                memory_change = abs(memory.percent - self.last_memory_percent)

                # Send updates if significant changes or periodically
                should_send = (cpu_change > 5 or memory_change > 5 or
                             self.system_queue.empty())

                if should_send:
                    message = BodyMessage.create_sensory(
                        sensor_type="system",
                        data={
                            "cpu_percent": cpu_percent,
                            "memory_percent": memory.percent,
                            "memory_used_gb": memory.used / (1024**3),
                            "memory_total_gb": memory.total / (1024**3),
                            "disk_percent": disk.percent,
                            "disk_free_gb": disk.free / (1024**3),
                            "timestamp": datetime.now().isoformat()
                        },
                        confidence=1.0
                    )
                    self._safe_put(self.system_queue, message)

                self.last_cpu_percent = cpu_percent
                self.last_memory_percent = memory.percent

                time.sleep(2)  # Update every 2 seconds

        except Exception as e:
            print(f"System monitoring error: {e}")

    def receive_text_input(self, text: str, source: str = "user"):
        """Receive text input from external sources."""
        message = BodyMessage.create_sensory(
            sensor_type="text",
            data={
                "text": text,
                "source": source,
                "timestamp": datetime.now().isoformat()
            },
            confidence=1.0
        )
        self._safe_put(self.text_queue, message)

    def get_sensory_data(self) -> Dict[str, List[BodyMessage]]:
        """Get all available sensory data."""
        data = {
            "vision": self._drain_queue(self.vision_queue),
            "audio": self._drain_queue(self.audio_queue),
            "text": self._drain_queue(self.text_queue),
            "system": self._drain_queue(self.system_queue)
        }
        return data

    def _safe_put(self, q: queue.Queue, item):
        """Safely put item in queue, dropping oldest if full."""
        try:
            q.put_nowait(item)
        except queue.Full:
            try:
                q.get_nowait()  # Remove oldest
                q.put_nowait(item)
            except:
                pass  # Queue operations failed

    def _drain_queue(self, q: queue.Queue) -> List:
        """Drain all items from a queue."""
        items = []
        while True:
            try:
                items.append(q.get_nowait())
            except queue.Empty:
                break
        return items

    def get_sensor_status(self) -> Dict[str, bool]:
        """Get status of all sensors."""
        return {
            "vision": self.vision_active,
            "audio": self.audio_active,
            "system": self.system_active,
            "text": True  # Always available
        }