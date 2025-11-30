"""
Motor System for Chappy's Digital Body

Handles all motor outputs:
- Speech: Text-to-speech synthesis
- Display: Visual outputs and screen rendering
- Actions: File operations, API calls, system commands
- Actuators: Hardware control (GPIO, USB devices)
"""

import subprocess
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import queue
import json
import requests

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import cv2
    import numpy as np
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

from ..message import BodyMessage


class MotorSystem:
    """Manages all motor outputs for Chappy's body."""

    def __init__(self):
        self.speech_active = False
        self.display_active = False
        self.action_active = False

        # Queues for different motor outputs
        self.speech_queue = queue.Queue(maxsize=10)
        self.display_queue = queue.Queue(maxsize=10)
        self.action_queue = queue.Queue(maxsize=10)

        # Processing threads
        self.speech_thread = None
        self.display_thread = None
        self.action_thread = None

        # TTS engine
        self.tts_engine = None

        # Display state
        self.display_window = None

    def initialize_motors(self) -> bool:
        """Initialize all available motor systems."""
        try:
            # Initialize speech
            if self._init_speech():
                self.speech_active = True
                print("✅ Speech motor initialized")

            # Initialize display
            if self._init_display():
                self.display_active = True
                print("✅ Display motor initialized")

            # Initialize actions
            self.action_active = True
            print("✅ Action motor initialized")

            return True
        except Exception as e:
            print(f"❌ Failed to initialize motors: {e}")
            return False

    def _init_speech(self) -> bool:
        """Initialize text-to-speech engine."""
        if not TTS_AVAILABLE:
            print("⚠️ pyttsx3 not available, speech disabled")
            return False

        try:
            self.tts_engine = pyttsx3.init()
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            self.tts_engine.setProperty('rate', 180)  # Speed of speech
            return True
        except Exception as e:
            print(f"Speech initialization failed: {e}")
            return False

    def _init_display(self) -> bool:
        """Initialize display/visual output system."""
        if not VISION_AVAILABLE:
            print("⚠️ OpenCV not available, display disabled")
            return False
        return True

    def start_motor_processing(self):
        """Start all motor processing threads."""
        if self.speech_active:
            self.speech_thread = threading.Thread(target=self._speech_loop, daemon=True)
            self.speech_thread.start()

        if self.display_active:
            self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
            self.display_thread.start()

        if self.action_active:
            self.action_thread = threading.Thread(target=self._action_loop, daemon=True)
            self.action_thread.start()

    def stop_motor_processing(self):
        """Stop all motor processing."""
        self.speech_active = False
        self.display_active = False
        self.action_active = False

        # Wait for threads to finish
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1.0)
        if self.action_thread and self.action_thread.is_alive():
            self.action_thread.join(timeout=1.0)

    def _speech_loop(self):
        """Main speech synthesis loop."""
        try:
            while self.speech_active:
                try:
                    # Get speech request
                    message = self.speech_queue.get(timeout=1.0)

                    if message.motor_type == "speech" and "text" in message.data:
                        text = message.data["text"]

                        if self.tts_engine:
                            print(f"🗣️ Speaking: {text[:50]}...")
                            self.tts_engine.say(text)
                            self.tts_engine.runAndWait()
                        else:
                            # Fallback to system TTS
                            try:
                                subprocess.run(["espeak", text],
                                             capture_output=True, timeout=10)
                            except:
                                print(f"Could not speak: {text[:50]}...")

                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Speech processing error: {e}")

        except Exception as e:
            print(f"Speech loop error: {e}")

    def _display_loop(self):
        """Main display/visual output loop."""
        try:
            while self.display_active:
                try:
                    # Get display request
                    message = self.display_queue.get(timeout=1.0)

                    if message.motor_type == "display":
                        self._handle_display_message(message)

                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Display processing error: {e}")

        except Exception as e:
            print(f"Display loop error: {e}")

    def _handle_display_message(self, message: BodyMessage):
        """Handle different types of display messages."""
        display_type = message.data.get("type", "text")

        if display_type == "text":
            # Print to console for now
            text = message.data.get("text", "")
            print(f"📺 Display: {text}")

        elif display_type == "image" and VISION_AVAILABLE:
            # Display image
            image_data = message.data.get("image")
            if image_data is not None:
                if isinstance(image_data, np.ndarray):
                    cv2.imshow("Chappy Display", image_data)
                    cv2.waitKey(3000)  # Show for 3 seconds
                    cv2.destroyAllWindows()

        elif display_type == "status":
            # Update status display
            status = message.data.get("status", {})
            print(f"📊 Status Update: {status}")

    def _action_loop(self):
        """Main action execution loop."""
        try:
            while self.action_active:
                try:
                    # Get action request
                    message = self.action_queue.get(timeout=1.0)

                    if message.motor_type == "action":
                        self._execute_action(message)

                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Action processing error: {e}")

        except Exception as e:
            print(f"Action loop error: {e}")

    def _execute_action(self, message: BodyMessage):
        """Execute different types of actions."""
        action_type = message.data.get("action_type")

        try:
            if action_type == "file_write":
                filepath = message.data.get("filepath")
                content = message.data.get("content", "")
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"📝 Wrote to file: {filepath}")

            elif action_type == "file_read":
                filepath = message.data.get("filepath")
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        content = f.read()
                    print(f"📖 Read from file: {filepath}")
                    # Could send result back via callback

            elif action_type == "command":
                command = message.data.get("command")
                if command:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                    print(f"⚡ Executed command: {command}")
                    if result.stdout:
                        print(f"Output: {result.stdout[:200]}...")

            elif action_type == "api_call":
                url = message.data.get("url")
                method = message.data.get("method", "GET")
                data = message.data.get("data")

                if method.upper() == "GET":
                    response = requests.get(url, timeout=10)
                elif method.upper() == "POST":
                    response = requests.post(url, json=data, timeout=10)
                else:
                    print(f"Unsupported HTTP method: {method}")
                    return

                print(f"🌐 API call to {url}: {response.status_code}")

            elif action_type == "gpio" or action_type == "hardware":
                # Placeholder for hardware control
                pin = message.data.get("pin")
                state = message.data.get("state")
                print(f"🔌 Hardware control: pin {pin} -> {state}")
                # Would integrate with GPIO libraries here

        except Exception as e:
            print(f"Action execution failed: {e}")

    def speak(self, text: str, priority: int = 0):
        """Queue text for speech synthesis."""
        message = BodyMessage.create_motor(
            motor_type="speech",
            data={"text": text},
            priority=priority
        )
        self._safe_put(self.speech_queue, message)

    def display(self, content: Any, display_type: str = "text", priority: int = 0):
        """Queue content for display."""
        message = BodyMessage.create_motor(
            motor_type="display",
            data={"content": content, "type": display_type},
            priority=priority
        )
        self._safe_put(self.display_queue, message)

    def execute_action(self, action_type: str, **kwargs):
        """Queue an action for execution."""
        data = {"action_type": action_type}
        data.update(kwargs)

        message = BodyMessage.create_motor(
            motor_type="action",
            data=data,
            priority=1  # Actions are typically high priority
        )
        self._safe_put(self.action_queue, message)

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

    def get_motor_status(self) -> Dict[str, bool]:
        """Get status of all motor systems."""
        return {
            "speech": self.speech_active,
            "display": self.display_active,
            "action": self.action_active
        }