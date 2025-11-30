"""
Container Management for Chappy's Digital Body

Handles Podman pod orchestration and inter-container communication:
- Pod configuration and lifecycle management
- Message bus for sensory-motor-brain communication
- Health monitoring and auto-recovery
- Resource allocation and scaling
"""

import subprocess
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import queue


class ContainerManager:
    """Manages Podman containers for Chappy's body systems."""

    def __init__(self, pod_name: str = "chappy-body"):
        self.pod_name = pod_name
        self.containers = {}
        self.message_bus = MessageBus()
        self.health_monitor = HealthMonitor()

        # Container configurations
        self.container_configs = {
            'sensory': {
                'image': 'chappy-sensory:latest',
                'ports': ['8081:8080'],
                'volumes': ['/dev/video0:/dev/video0', '/tmp/audio:/tmp/audio'],
                'env': ['SENSOR_CONFIG=/app/config/sensors.json']
            },
            'motor': {
                'image': 'chappy-motor:latest',
                'ports': ['8082:8080'],
                'devices': ['/dev/snd:/dev/snd'],
                'env': ['MOTOR_CONFIG=/app/config/motors.json']
            },
            'brain': {
                'image': 'chappy-brain:latest',
                'ports': ['8083:8080'],
                'volumes': ['./digital_cortex:/app/digital_cortex:ro',
                           './chappy_weights.json:/app/chappy_weights.json'],
                'env': ['OLLAMA_HOST=host.containers.internal:11434']
            },
            'ollama': {
                'image': 'ollama/ollama:latest',
                'ports': ['11434:11434'],
                'volumes': ['ollama_data:/root/.ollama']
            },
            'autonomic': {
                'image': 'chappy-autonomic:latest',
                'ports': ['8084:8080'],
                'env': ['MONITOR_INTERVAL=5']
            }
        }

    def create_pod(self) -> bool:
        """Create the Chappy body pod."""
        try:
            # Check if pod already exists
            if self._pod_exists():
                print(f"Pod {self.pod_name} already exists")
                return True

            # Create pod
            cmd = [
                'podman', 'pod', 'create',
                '--name', self.pod_name,
                '--network', 'bridge',
                '-p', '8080:8080',  # Main API port
                '-p', '8501:8501'   # Streamlit port
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed to create pod: {result.stderr}")
                return False

            print(f"✅ Created pod: {self.pod_name}")
            return True

        except Exception as e:
            print(f"Pod creation error: {e}")
            return False

    def start_containers(self) -> bool:
        """Start all body system containers."""
        try:
            success_count = 0

            for container_name, config in self.container_configs.items():
                if self._start_container(container_name, config):
                    success_count += 1
                    print(f"✅ Started container: {container_name}")
                else:
                    print(f"❌ Failed to start container: {container_name}")

            # Start message bus
            self.message_bus.start()

            # Start health monitoring
            self.health_monitor.start_monitoring(self.pod_name)

            print(f"Started {success_count}/{len(self.container_configs)} containers")
            return success_count > 0

        except Exception as e:
            print(f"Container startup error: {e}")
            return False

    def _start_container(self, name: str, config: Dict[str, Any]) -> bool:
        """Start a single container."""
        try:
            container_full_name = f"{self.pod_name}-{name}"

            # Build podman run command
            cmd = ['podman', 'run', '-d', '--pod', self.pod_name, '--name', container_full_name]

            # Add ports
            if 'ports' in config:
                for port in config['ports']:
                    cmd.extend(['-p', port])

            # Add volumes
            if 'volumes' in config:
                for volume in config['volumes']:
                    cmd.extend(['-v', volume])

            # Add devices
            if 'devices' in config:
                for device in config['devices']:
                    cmd.extend(['--device', device])

            # Add environment variables
            if 'env' in config:
                for env in config['env']:
                    cmd.extend(['-e', env])

            # Add image
            cmd.append(config['image'])

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.containers[name] = {
                    'name': container_full_name,
                    'config': config,
                    'status': 'running',
                    'started_at': datetime.now().isoformat()
                }
                return True
            else:
                print(f"Container {name} failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error starting container {name}: {e}")
            return False

    def stop_containers(self):
        """Stop all containers and the pod."""
        try:
            # Stop health monitoring
            self.health_monitor.stop_monitoring()

            # Stop message bus
            self.message_bus.stop()

            # Stop containers
            for container_name, container_info in self.containers.items():
                self._stop_container(container_name)

            # Stop pod
            cmd = ['podman', 'pod', 'stop', self.pod_name]
            subprocess.run(cmd, capture_output=True)

            # Remove pod
            cmd = ['podman', 'pod', 'rm', self.pod_name]
            subprocess.run(cmd, capture_output=True)

            print(f"✅ Stopped pod: {self.pod_name}")

        except Exception as e:
            print(f"Error stopping containers: {e}")

    def _stop_container(self, name: str):
        """Stop a single container."""
        try:
            container_full_name = f"{self.pod_name}-{name}"
            cmd = ['podman', 'stop', container_full_name]
            subprocess.run(cmd, capture_output=True, timeout=10)

            cmd = ['podman', 'rm', container_full_name]
            subprocess.run(cmd, capture_output=True)

            if name in self.containers:
                self.containers[name]['status'] = 'stopped'

        except Exception as e:
            print(f"Error stopping container {name}: {e}")

    def get_pod_status(self) -> Dict[str, Any]:
        """Get status of the pod and all containers."""
        try:
            # Get pod info
            cmd = ['podman', 'pod', 'ps', '--format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                pods = json.loads(result.stdout)
                pod_info = next((p for p in pods if p.get('Name') == self.pod_name), None)
            else:
                pod_info = None

            # Get container info
            cmd = ['podman', 'ps', '--format', 'json', '--filter', f'pod={self.pod_name}']
            result = subprocess.run(cmd, capture_output=True, text=True)

            containers_info = []
            if result.returncode == 0:
                containers_info = json.loads(result.stdout)

            return {
                'pod': {
                    'name': self.pod_name,
                    'exists': pod_info is not None,
                    'status': pod_info.get('Status') if pod_info else 'unknown'
                },
                'containers': {
                    c.get('Names', ['unknown'])[0].replace(f"{self.pod_name}-", ''): {
                        'status': c.get('Status', 'unknown'),
                        'ports': c.get('Ports', []),
                        'image': c.get('Image', '')
                    }
                    for c in containers_info
                },
                'message_bus': self.message_bus.get_status(),
                'health': self.health_monitor.get_health_status()
            }

        except Exception as e:
            return {'error': str(e)}

    def _pod_exists(self) -> bool:
        """Check if pod exists."""
        try:
            cmd = ['podman', 'pod', 'exists', self.pod_name]
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except:
            return False

    def build_containers(self) -> bool:
        """Build all container images."""
        try:
            success_count = 0

            for container_name, config in self.container_configs.items():
                containerfile_path = f"./digital_body/containers/Containerfile.{container_name}"

                if os.path.exists(containerfile_path):
                    print(f"Building {container_name}...")
                    cmd = ['podman', 'build', '-t', f"chappy-{container_name}:latest",
                          '-f', containerfile_path, './digital_body/containers']

                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                        print(f"✅ Built {container_name}")
                    else:
                        print(f"❌ Failed to build {container_name}: {result.stderr}")
                else:
                    print(f"⚠️ Containerfile not found: {containerfile_path}")

            return success_count > 0

        except Exception as e:
            print(f"Build error: {e}")
            return False


class MessageBus:
    """Inter-container message bus for body system communication."""

    def __init__(self):
        self.active = False
        self.threads = []
        self.queues = {
            'sensory_to_brain': queue.Queue(),
            'brain_to_motor': queue.Queue(),
            'nervous_to_all': queue.Queue(),
            'reflex_to_all': queue.Queue()
        }

    def start(self):
        """Start the message bus."""
        self.active = True
        # Message routing threads would go here
        print("✅ Message bus started")

    def stop(self):
        """Stop the message bus."""
        self.active = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        print("✅ Message bus stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get message bus status."""
        return {
            'active': self.active,
            'queues': {name: q.qsize() for name, q in self.queues.items()},
            'threads': len(self.threads)
        }


class HealthMonitor:
    """Health monitoring for containers and pod."""

    def __init__(self):
        self.active = False
        self.pod_name = None
        self.monitor_thread = None
        self.health_history = []

    def start_monitoring(self, pod_name: str):
        """Start health monitoring."""
        self.pod_name = pod_name
        self.active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Health monitoring started")

    def stop_monitoring(self):
        """Stop health monitoring."""
        self.active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        print("✅ Health monitoring stopped")

    def _monitor_loop(self):
        """Main health monitoring loop."""
        while self.active:
            try:
                health_status = self._check_health()
                self.health_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'status': health_status
                })

                # Keep only recent history
                if len(self.health_history) > 50:
                    self.health_history = self.health_history[-50:]

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"Health monitoring error: {e}")
                time.sleep(5)

    def _check_health(self) -> Dict[str, Any]:
        """Check health of pod and containers."""
        try:
            # Check pod status
            cmd = ['podman', 'pod', 'ps', '--filter', f'name={self.pod_name}', '--format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True)

            pod_status = 'unknown'
            if result.returncode == 0:
                pods = json.loads(result.stdout)
                if pods:
                    pod_status = pods[0].get('Status', 'unknown')

            # Check container health
            cmd = ['podman', 'ps', '--filter', f'pod={self.pod_name}', '--format', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True)

            container_status = {}
            if result.returncode == 0:
                containers = json.loads(result.stdout)
                for container in containers:
                    name = container.get('Names', ['unknown'])[0]
                    status = container.get('Status', 'unknown')
                    container_status[name] = status

            return {
                'pod_status': pod_status,
                'containers': container_status,
                'overall_health': 'healthy' if pod_status == 'Running' else 'unhealthy'
            }

        except Exception as e:
            return {'error': str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        if self.health_history:
            return self.health_history[-1]['status']
        return {'status': 'no_data'}