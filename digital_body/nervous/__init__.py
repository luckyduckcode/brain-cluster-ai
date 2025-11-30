"""
Nervous System for Chappy's Digital Body

Handles feedback loops and regulatory functions:
- Proprioception: Self-awareness of body state
- Pain/Pleasure: Error signals vs success signals
- Homeostasis: Resource management, sleep/wake cycles
- Reflexes: Fast-path responses that bypass full cortex processing
"""

import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
import threading
import queue
import json

from ..message import BodyMessage


class NervousSystem:
    """Manages nervous system functions for Chappy's body."""

    def __init__(self):
        self.active = False

        # Physiological state
        self.energy_level = 100.0  # 0-100
        self.stress_level = 0.0    # 0-100
        self.pain_signals = []
        self.pleasure_signals = []

        # Homeostasis parameters
        self.target_cpu_percent = 50.0
        self.target_memory_percent = 70.0
        self.sleep_threshold = 20.0  # Energy level to trigger sleep
        self.wake_threshold = 80.0   # Energy level to wake up

        # Reflex system
        self.reflexes = {}
        self.reflex_active = False

        # Queues
        self.nervous_queue = queue.Queue(maxsize=20)
        self.reflex_queue = queue.Queue(maxsize=5)

        # Monitoring thread
        self.monitor_thread = None

        # State history for trends
        self.state_history = []
        self.max_history = 100

    def initialize_nervous_system(self) -> bool:
        """Initialize the nervous system."""
        try:
            # Set up basic reflexes
            self._setup_reflexes()

            self.active = True
            print("✅ Nervous system initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize nervous system: {e}")
            return False

    def _setup_reflexes(self):
        """Set up automatic reflex responses."""
        # High CPU reflex
        self.add_reflex(
            name="high_cpu_reflex",
            condition=lambda state: state.get('cpu_percent', 0) > 90,
            action=self._cpu_throttle_reflex,
            priority=2
        )

        # Low memory reflex
        self.add_reflex(
            name="low_memory_reflex",
            condition=lambda state: state.get('memory_percent', 0) > 95,
            action=self._memory_cleanup_reflex,
            priority=2
        )

        # System error reflex
        self.add_reflex(
            name="error_reflex",
            condition=lambda state: state.get('error_count', 0) > 5,
            action=self._error_recovery_reflex,
            priority=3
        )

        # Sleep reflex
        self.add_reflex(
            name="sleep_reflex",
            condition=lambda state: self.energy_level < self.sleep_threshold,
            action=self._sleep_reflex,
            priority=1
        )

    def add_reflex(self, name: str, condition: Callable, action: Callable, priority: int = 1):
        """Add a reflex response."""
        self.reflexes[name] = {
            'condition': condition,
            'action': action,
            'priority': priority,
            'last_triggered': None,
            'cooldown': 30  # seconds between triggers
        }

    def start_nervous_processing(self):
        """Start nervous system processing."""
        if self.active:
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

            self.reflex_thread = threading.Thread(target=self._reflex_loop, daemon=True)
            self.reflex_thread.start()

    def stop_nervous_processing(self):
        """Stop nervous system processing."""
        self.active = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        if hasattr(self, 'reflex_thread') and self.reflex_thread.is_alive():
            self.reflex_thread.join(timeout=1.0)

    def _monitor_loop(self):
        """Main monitoring and homeostasis loop."""
        try:
            while self.active:
                # Get current system state
                state = self._get_system_state()

                # Update physiological state
                self._update_physiological_state(state)

                # Check homeostasis
                self._check_homeostasis(state)

                # Store state history
                self.state_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'state': state,
                    'energy': self.energy_level,
                    'stress': self.stress_level
                })

                # Keep history bounded
                if len(self.state_history) > self.max_history:
                    self.state_history = self.state_history[-self.max_history:]

                # Send proprioception message
                proprioception_msg = BodyMessage.create_nervous(
                    nervous_type="proprioception",
                    data={
                        'energy_level': self.energy_level,
                        'stress_level': self.stress_level,
                        'system_state': state,
                        'pain_signals': len(self.pain_signals),
                        'pleasure_signals': len(self.pleasure_signals)
                    },
                    confidence=1.0
                )
                self._safe_put(self.nervous_queue, proprioception_msg)

                time.sleep(5)  # Monitor every 5 seconds

        except Exception as e:
            print(f"Nervous system monitoring error: {e}")

    def _reflex_loop(self):
        """Reflex processing loop - high priority responses."""
        try:
            while self.active:
                # Get current state for reflex checking
                state = self._get_system_state()

                # Check all reflexes
                for reflex_name, reflex in self.reflexes.items():
                    try:
                        # Check cooldown
                        if reflex['last_triggered']:
                            time_since_trigger = (datetime.now() - reflex['last_triggered']).seconds
                            if time_since_trigger < reflex['cooldown']:
                                continue

                        # Check condition
                        if reflex['condition'](state):
                            # Trigger reflex
                            reflex_msg = reflex['action'](state)
                            if reflex_msg:
                                self._safe_put(self.reflex_queue, reflex_msg)
                                reflex['last_triggered'] = datetime.now()
                                print(f"⚡ Reflex triggered: {reflex_name}")

                    except Exception as e:
                        print(f"Reflex {reflex_name} error: {e}")

                time.sleep(1)  # Check reflexes every second

        except Exception as e:
            print(f"Reflex loop error: {e}")

    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state for monitoring."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Count recent errors (would need integration with error logging)
            error_count = getattr(self, '_error_count', 0)

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'disk_percent': disk.percent,
                'error_count': error_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

    def _update_physiological_state(self, state: Dict[str, Any]):
        """Update Chappy's physiological state based on system conditions."""
        # Energy level based on resource usage
        cpu_factor = max(0, 1 - (state.get('cpu_percent', 0) / 100))
        memory_factor = max(0, 1 - (state.get('memory_percent', 0) / 100))

        # Energy decreases with high resource usage, increases during idle
        energy_change = (cpu_factor + memory_factor) / 2 * 2 - 1  # -1 to +1
        self.energy_level = max(0, min(100, self.energy_level + energy_change))

        # Stress level based on system pressure
        stress_factors = [
            state.get('cpu_percent', 0) / 100,
            state.get('memory_percent', 0) / 100,
            min(state.get('error_count', 0) / 10, 1)  # Cap at 10 errors
        ]
        self.stress_level = sum(stress_factors) / len(stress_factors) * 100

    def _check_homeostasis(self, state: Dict[str, Any]):
        """Check and maintain system homeostasis."""
        issues = []

        # CPU homeostasis
        if state.get('cpu_percent', 0) > self.target_cpu_percent + 20:
            issues.append("high_cpu")

        # Memory homeostasis
        if state.get('memory_percent', 0) > self.target_memory_percent + 10:
            issues.append("high_memory")

        # Send homeostasis message if issues found
        if issues:
            homeostasis_msg = BodyMessage.create_nervous(
                nervous_type="homeostasis",
                data={
                    'issues': issues,
                    'current_state': state,
                    'recommendations': self._get_homeostasis_recommendations(issues)
                },
                confidence=0.9
            )
            self._safe_put(self.nervous_queue, homeostasis_msg)

    def _get_homeostasis_recommendations(self, issues: List[str]) -> List[str]:
        """Get recommendations for homeostasis issues."""
        recommendations = []

        if "high_cpu" in issues:
            recommendations.extend([
                "Reduce concurrent operations",
                "Increase processing intervals",
                "Consider background processing"
            ])

        if "high_memory" in issues:
            recommendations.extend([
                "Clear old sensory data",
                "Reduce memory cache size",
                "Implement memory cleanup"
            ])

        return recommendations

    def _cpu_throttle_reflex(self, state: Dict[str, Any]) -> BodyMessage:
        """Reflex response to high CPU usage."""
        return BodyMessage.create_reflex(
            reflex_type="cpu_throttle",
            data={
                'action': 'reduce_processing',
                'reason': f'CPU at {state.get("cpu_percent", 0):.1f}%',
                'recommendations': ['Pause non-essential processing', 'Reduce thread count']
            }
        )

    def _memory_cleanup_reflex(self, state: Dict[str, Any]) -> BodyMessage:
        """Reflex response to high memory usage."""
        return BodyMessage.create_reflex(
            reflex_type="memory_cleanup",
            data={
                'action': 'clear_memory',
                'reason': f'Memory at {state.get("memory_percent", 0):.1f}%',
                'recommendations': ['Clear sensory buffers', 'Reduce cache sizes']
            }
        )

    def _error_recovery_reflex(self, state: Dict[str, Any]) -> BodyMessage:
        """Reflex response to high error rate."""
        return BodyMessage.create_reflex(
            reflex_type="error_recovery",
            data={
                'action': 'reset_components',
                'reason': f'{state.get("error_count", 0)} recent errors',
                'recommendations': ['Restart failing components', 'Clear error state']
            }
        )

    def _sleep_reflex(self, state: Dict[str, Any]) -> BodyMessage:
        """Reflex response to low energy."""
        return BodyMessage.create_reflex(
            reflex_type="enter_sleep",
            data={
                'action': 'sleep_mode',
                'reason': f'Energy level at {self.energy_level:.1f}%',
                'duration': 'until_energy_restored'
            }
        )

    def signal_pain(self, source: str, intensity: float, reason: str):
        """Record a pain signal."""
        pain_signal = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'intensity': intensity,
            'reason': reason
        }
        self.pain_signals.append(pain_signal)

        # Keep only recent signals
        cutoff = datetime.now() - timedelta(minutes=5)
        self.pain_signals = [s for s in self.pain_signals
                           if datetime.fromisoformat(s['timestamp']) > cutoff]

        # Send pain message
        pain_msg = BodyMessage.create_nervous(
            nervous_type="pain",
            data=pain_signal,
            confidence=1.0,
            priority=2
        )
        self._safe_put(self.nervous_queue, pain_msg)

    def signal_pleasure(self, source: str, intensity: float, reason: str):
        """Record a pleasure signal."""
        pleasure_signal = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'intensity': intensity,
            'reason': reason
        }
        self.pleasure_signals.append(pleasure_signal)

        # Keep only recent signals
        cutoff = datetime.now() - timedelta(minutes=5)
        self.pleasure_signals = [s for s in self.pleasure_signals
                               if datetime.fromisoformat(s['timestamp']) > cutoff]

        # Send pleasure message
        pleasure_msg = BodyMessage.create_nervous(
            nervous_type="pleasure",
            data=pleasure_signal,
            confidence=1.0,
            priority=1
        )
        self._safe_put(self.nervous_queue, pleasure_msg)

    def get_nervous_data(self) -> Dict[str, List[BodyMessage]]:
        """Get all available nervous system data."""
        return {
            "nervous": self._drain_queue(self.nervous_queue),
            "reflexes": self._drain_queue(self.reflex_queue)
        }

    def get_physiological_state(self) -> Dict[str, Any]:
        """Get current physiological state."""
        return {
            'energy_level': self.energy_level,
            'stress_level': self.stress_level,
            'pain_signals': len(self.pain_signals),
            'pleasure_signals': len(self.pleasure_signals),
            'active_reflexes': len([r for r in self.reflexes.values()
                                   if r['last_triggered'] and
                                   (datetime.now() - r['last_triggered']).seconds < 60])
        }

    def _safe_put(self, q: queue.Queue, item):
        """Safely put item in queue, dropping oldest if full."""
        try:
            q.put_nowait(item)
        except queue.Full:
            try:
                q.get_nowait()  # Remove oldest
                q.put_nowait(item)
            except:
                pass

    def _drain_queue(self, q: queue.Queue) -> List:
        """Drain all items from a queue."""
        items = []
        while True:
            try:
                items.append(q.get_nowait())
            except queue.Empty:
                break
        return items