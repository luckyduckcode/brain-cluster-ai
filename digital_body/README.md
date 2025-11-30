# Chappy's Digital Body Architecture

A complete embodied AI system that gives Chappy sensory inputs, motor outputs, and nervous system feedback loops through a containerized Podman pod architecture.

## 🏗️ Architecture Overview

Chappy's digital body consists of four main systems working together:

### SENSORY SYSTEMS (Input)
- **Vision**: Camera/webcam feed with motion detection
- **Audio**: Microphone input with speech-to-text processing
- **Text**: Chat/API inputs from external sources
- **System**: Resource monitoring (CPU, memory, disk usage)

### MOTOR SYSTEMS (Output)
- **Speech**: Text-to-speech synthesis with voice configuration
- **Display**: Visual outputs and screen rendering
- **Actions**: File operations, API calls, system commands
- **Hardware**: GPIO/USB device control (extensible)

### NERVOUS SYSTEM (Feedback Loops)
- **Proprioception**: Self-awareness of body state and energy levels
- **Pain/Pleasure**: Error signals vs success signals
- **Homeostasis**: Resource management and system balance
- **Reflexes**: Fast-path responses bypassing full cortex processing

### CONTAINER ARCHITECTURE
```
chappy-body-pod/
├── sensory-container     # Vision, audio, system monitoring
├── motor-container      # Speech, display, action execution
├── brain-container      # Digital Cortex integration
├── ollama-container     # LLM backend service
└── autonomic-container  # Health monitoring & regulation
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# System dependencies
sudo apt-get install podman python3-opencv portaudio19-dev

# Python dependencies
pip install opencv-python speechrecognition pyttsx3 flask psutil
```

### 2. Test the Digital Body
```bash
cd /home/duck/Documents/brain\ cluster\ ai
python3 test_digital_body.py
```

### 3. Build and Run Containers (Optional)
```bash
# Build container images
cd digital_body/containers
podman build -t chappy-sensory:latest -f Containerfile.sensory .

# Create and start pod
python3 -c "
from digital_body.containers import ContainerManager
mgr = ContainerManager()
mgr.create_pod()
mgr.start_containers()
"
```

## 📖 Usage Examples

### Basic Body Integration
```python
from digital_body import SensorySystem, MotorSystem, NervousSystem

# Initialize systems
sensory = SensorySystem()
motor = MotorSystem()
nervous = NervousSystem()

# Start all systems
sensory.initialize_sensors()
motor.initialize_motors()
nervous.initialize_nervous_system()

sensory.start_sensory_processing()
motor.start_motor_processing()
nervous.start_nervous_processing()

# Send text input
sensory.receive_text_input('Hello Chappy!')

# Make Chappy speak
motor.speak('Hello! I can see and hear you!')

# Check nervous system state
state = nervous.get_physiological_state()
print(f'Energy: {state[\"energy_level\"]}%, Stress: {state[\"stress_level\"]}%')
```

### Container Management
```python
from digital_body.containers import ContainerManager

# Create container manager
mgr = ContainerManager('my-chappy-body')

# Build and start all containers
mgr.build_containers()
mgr.create_pod()
mgr.start_containers()

# Check status
status = mgr.get_pod_status()
print(f'Pod healthy: {status[\"pod\"][\"status\"] == \"Running\"}')
```

### Message System
```python
from digital_body.message import BodyMessage

# Create sensory message
vision_msg = BodyMessage.create_sensory(
    sensor_type='vision',
    data={'motion_detected': True, 'frame_shape': [640, 480]},
    confidence=0.85
)

# Create motor message
speech_msg = BodyMessage.create_motor(
    motor_type='speech',
    data={'text': 'I detected motion!'},
    confidence=0.9
)

# Create nervous message
pain_msg = BodyMessage.create_nervous(
    nervous_type='pain',
    data={'intensity': 0.7, 'reason': 'High CPU usage'},
    confidence=1.0
)
```

## 🔧 Configuration

### Sensor Configuration (`containers/config/sensors.json`)
```json
{
  "vision": {
    "enabled": true,
    "device": "/dev/video0",
    "resolution": [640, 480],
    "fps": 10,
    "motion_threshold": 0.01
  },
  "audio": {
    "enabled": true,
    "sample_rate": 16000,
    "language": "en-US"
  }
}
```

### Reflex Configuration
```python
# Add custom reflexes
nervous.add_reflex(
    name="custom_reflex",
    condition=lambda state: state.get('custom_metric', 0) > threshold,
    action=custom_handler,
    priority=1
)
```

## 🧠 Nervous System Features

### Reflexes
Automatic responses to system conditions:
- **High CPU Reflex**: Reduces processing when CPU > 90%
- **Memory Cleanup Reflex**: Clears buffers when memory > 95%
- **Error Recovery Reflex**: Resets components after errors
- **Sleep Reflex**: Enters low-power mode when energy is low

### Homeostasis
Maintains system balance:
- CPU usage regulation
- Memory management
- Energy level monitoring
- Stress level tracking

### Proprioception
Self-awareness features:
- Real-time system state monitoring
- Energy and stress level tracking
- Pain/pleasure signal processing
- Physiological state reporting

## 🐳 Container Services

### Sensory Container
- **Port**: 8081
- **Endpoints**:
  - `GET /health` - Health check
  - `GET /status` - Sensor status
  - `GET /data` - Sensory data
  - `POST /text` - Receive text input

### Motor Container
- **Port**: 8082
- **Capabilities**: Speech synthesis, display, action execution

### Autonomic Container
- **Port**: 8084
- **Features**: Health monitoring, resource regulation, auto-recovery

## 🔄 Message Bus

Inter-container communication system:
- **Queues**: sensory_to_brain, brain_to_motor, nervous_to_all, reflex_to_all
- **Message Types**: sensory, motor, nervous, reflex
- **Priority Levels**: 0=normal, 1=high, 2=critical

## 🧪 Testing

Run the comprehensive test suite:
```bash
python3 test_digital_body.py
```

This tests:
- ✅ System initialization
- ✅ Sensory input processing
- ✅ Motor output generation
- ✅ Nervous system reflexes
- ✅ Message flow between systems
- ✅ Container management API

## 🚀 Integration with Brain

The digital body integrates seamlessly with Chappy's brain:

```python
# In chappy_gui.py or API
from digital_body import SensorySystem, MotorSystem, NervousSystem

# Add to ChappyBrainGUI class
def __init__(self):
    # ... existing code ...
    self.body_sensory = SensorySystem()
    self.body_motor = MotorSystem()
    self.body_nervous = NervousSystem()

# Process through body systems
def process_with_body(self, user_input):
    # Send to sensory
    self.body_sensory.receive_text_input(user_input)

    # Get brain response
    response = self.process_input(user_input)

    # Send to motor
    self.body_motor.speak(response)

    # Check nervous state
    state = self.body_nervous.get_physiological_state()
    if state['stress_level'] > 80:
        self.add_thought("😰", "I'm feeling stressed - might need a break", "nervous")
```

## 🔮 Future Extensions

- **Hardware Integration**: GPIO control for robotics
- **Multi-Modal Learning**: Vision + audio processing
- **Distributed Bodies**: Multiple body instances
- **Advanced Reflexes**: Learning-based reflex adaptation
- **Emotional Modeling**: Mood-based system responses

## 📊 Monitoring

Real-time monitoring capabilities:
- System resource usage
- Container health status
- Message bus throughput
- Reflex trigger frequency
- Physiological state trends

---

**Status**: ✅ Complete and tested
**Integration**: Ready for production use
**Extensibility**: Designed for hardware and distributed deployment