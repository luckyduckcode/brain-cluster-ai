# 🧠 Digital Cortex - Bio-Mimetic AGI System

A brain-inspired multi-agent AI architecture using local LLMs as "neurons" and specialized neural networks as "brain regions."

## 🎯 What We've Built (Major Milestones Complete!)

### ✅ **Digital Body Architecture - COMPLETE**
**Status:** 100% Complete

**What was built:**
- **Container Architecture**: Multi-container pod with sensory/motor/brain/autonomic containers
- **Message Bus**: Inter-container communication for sensory-motor-brain feedback loops
- **Health Monitoring**: Resource usage, component status, auto-regulation
- **Digital Body Integration**: Complete embodied AI system with all brain regions

### ✅ **YouTube Learning System - COMPLETE**
**Status:** 100% Complete

**What was built:**
- **Video Acquisition**: YouTube download, frame extraction, audio processing
- **Multimodal Sensorium**: Vision (LLaVA), Audio (Whisper STT), Text (captions/OCR)
- **Learning Orchestration**: Parallel processing, consensus synthesis, knowledge extraction
- **Memory Integration**: Store concepts, facts, procedures in Memory Palace
- **Knowledge Retrieval**: Query and apply learned video knowledge
- **Container Integration**: Video processing container with GPU acceleration

**Usage:**
```bash
# Learn from a YouTube video
"learn from video: https://youtube.com/watch?v=VIDEO_ID"

# Query learned knowledge
"what do you know about machine learning?"
"find videos about neural networks"
"learning stats"
```

### ✅ Core Components Implemented

1. **Message Protocol** (`utils/message.py`)
   - Standardized communication format for all components
   - JSON-serializable with source, content, confidence, and timestamp
   - Validation and factory methods

2. **Corpus Colosseum** (`corpus_colosseum/colosseum.py`)
   - Short-term working memory with consensus mechanism
   - DBSCAN clustering for finding convergence among outputs
   - Weighted voting based on confidence scores
   - Automatic reset and capacity management

3. **LLM-Neuron Interface** (`utils/llm_neuron.py`)
   - Connects local Ollama models as processing neurons
   - Confidence score extraction from LLM outputs
   - NeuronPool for managing multiple specialized neurons
   - Support for different system prompts and temperatures

4. **Integration Demo** (`demo_integration.py`)
   - Complete end-to-end demonstration
   - Snake vs Garden Hose scenario from white paper
   - 4 specialized neurons (2 threat-focused, 2 logic-focused)
   - Real-time consensus finding

## 🚀 Quick Start

### Prerequisites
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama3.2:1b          # Main reasoning model
ollama pull llava:7b             # Vision processing (for video learning)

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install ffmpeg       # For video processing

# Install Python dependencies
pip install -r requirements.txt
```

**Additional Models for Full Functionality:**
- `llava:7b` - Vision-language model for video frame analysis
- `whisper` - Audio transcription (handled by yt-dlp integration)

### 🖥️ **Standalone Desktop App - NEW!**
**Status:** Complete - Simple & User-Friendly

**What was built:**
- **Clean Interface**: Simple, welcoming desktop app focused on chat
- **Easy Chat**: Large chat area with clear message formatting
- **Smart Initialization**: Background brain loading with status updates
- **User-Friendly Design**: No complex tabs, just chat and status
- **Modern UI**: CustomTkinter with automatic themes

**Features:**
- 💬 **Simple Chat Interface**: Clean, easy-to-use chat with Chappy
- 🧠 **Smart AI Companion**: Brain-inspired multimodal AI with personality
- 🎨 **Modern UI**: Automatic dark/light theme with friendly design
- ⚡ **Fast Startup**: Quick initialization with clear status messages
- 🎯 **User-Friendly**: No complex tabs or technical jargon

**Usage:**
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the simple desktop app
python3 launch_chappy_standalone.py

# Or run directly
python3 chappy_standalone_simple.py

# Test the installation
python3 test_standalone.py
```

**What You'll See:**
- **Welcome Screen**: Friendly greeting and introduction
- **Chat Area**: Large, clear chat window for conversations
- **Input Box**: Simple text entry with big "Send" button
- **Status Bar**: Clear messages about Chappy's brain status

**Perfect for:**
- First-time AI users
- Casual conversations with AI
- Educational demonstrations
- Quick AI interactions

**Features:**
- 💬 Real-time chat with Chappy's multimodal brain
- 🎥 One-click YouTube video learning with progress tracking
- 🧠 Memory palace visualization and management
- 📊 Live system monitoring and brain status
- 🎨 Modern UI with automatic dark/light theme detection
- ⌨️ Keyboard shortcuts (Ctrl+N for new chat, Ctrl+Q to quit)
- 💾 Conversation saving and export capabilities
- 🔄 Brain restart and settings management

**System Requirements:**
- Python 3.12+
- 4GB RAM minimum, 8GB recommended
- Ollama with llama3.2:1b model
- For video learning: ffmpeg, yt-dlp, OpenCV

**Desktop Integration (Linux):**
```bash
# Copy desktop entry to applications
cp chappy.desktop ~/.local/share/applications/

# Create icon (256x256 PNG recommended)
# Save as: chappy_icon.png in project root
# Then search for "Chappy AI" in your app launcher
```

### 🌐 Web Interface (Legacy)
```bash
# Install dependencies
pip install -r requirements.txt

# Launch web interface
python3 launch_chappy.py
# Then open http://localhost:8501
```

### REST API
```bash
# Install dependencies (includes FastAPI)
pip install -r requirements.txt

# Launch REST API
python3 launch_api.py
# or
./launch_api.sh
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Observability Dashboard
```bash
# Install dependencies (includes Streamlit, Plotly)
pip install -r requirements.txt

# Launch observability dashboard (requires API to be running)
python3 launch_dashboard.py
# or
./launch_dashboard.sh
# Dashboard available at http://localhost:8501
# Make sure API server is running on http://localhost:8000
```

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: ./venv/bin/activate

# Install dependencies (includes video processing libraries)
pip install -r requirements.txt

# Install additional video processing dependencies
pip install yt-dlp opencv-python

# For GPU acceleration (optional)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Run Tests
```bash
# Test Corpus Colosseum (no LLM required)
./venv/bin/python digital_cortex/tests/test_colosseum.py

# Test LLM-Neuron connectivity
./venv/bin/python digital_cortex/test_neuron_quick.py

# Run full integration demo (requires Ollama)
./venv/bin/python digital_cortex/demo_integration.py
```

### 🎨 Chappy the Brain Cluster GUI

Experience Chappy thinking out loud with an interactive web interface!

```bash
# Install additional GUI dependencies
pip install streamlit>=1.28.0

# Launch Chappy's GUI
python launch_chappy.py
```

### 🖥️ Chappy Desktop App

Run Chappy as a standalone desktop application with his own native window!

**Features:**
- Native desktop window (no browser required)
- Auto-starts Chappy's brain server
- Embedded web interface in desktop app
- Cross-platform support (Linux, Mac, Windows)
- Auto-prompt feature (Chappy thinks when idle)
- Memory integration and live thought streaming

**Quick Launch:**
```bash
# Linux/Mac
./launch_chappy_desktop.sh

# Windows
launch_chappy_desktop.bat

# Or directly
python3 chappy_desktop.py
```

**System Requirements:**
- Python 3.8+
- Ollama running with llama3.2:1b model
- Desktop environment (X11, Wayland, or Windows)

**Features:**
- 🗣️ **Real-time chat** with Chappy
- 🧠 **Live thought stream** showing brain activity
- 📊 **Brain status monitor** with component health
- 🎯 **Executive decisions** and meta-cognition display
- 💭 **Memory palace** visualization
- 🔴 **Live processing** through all brain regions

**What Chappy Can Do:**
- Answer questions and hold conversations
- Show his thought process through each brain region
- Learn from interactions and remember conversations
- Make executive decisions when faced with uncertainty
- Express emotions and assess situations
- **🎥 Watch and learn from YouTube videos** through multimodal processing
- **📚 Recall and apply knowledge** learned from educational videos
- **🧠 Build knowledge base** from video content with structured extraction

## 🌐 REST API

Integrate Chappy into your applications with a full REST API!

**Quick Launch:**
```bash
# Install dependencies
pip install -r requirements.txt

# Launch API server
python3 launch_api.py
# or
./launch_api.sh

# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

**API Endpoints:**

### `POST /api/v1/query`
Process a query through Chappy's brain.

**Request:**
```json
{
  "query": "What is the meaning of life?",
  "max_memories": 5,
  "include_thoughts": false
}
```

**Response:**
```json
{
  "response": "My friend, the meaning of life...",
  "confidence": 0.85,
  "processing_time": 2.34,
  "memory_count": 3,
  "consensus_reached": true
}
```

### `GET /api/v1/status`
Get system status and health information.

### `GET /api/v1/memories`
Retrieve recent memories from Chappy's memory palace.

### `POST /api/v1/feedback`
Provide feedback on responses to help Chappy learn.

**Features:**
- 🚀 **FastAPI** framework with automatic OpenAPI docs
- 📊 **Real-time processing** through all brain regions
- 🧠 **Memory integration** for contextual responses
- 💬 **Thought process** optional detailed output
- 🔄 **CORS enabled** for web integration
- 📈 **Performance metrics** and processing times

## 📊 Observability Dashboard

Monitor Chappy's brain activity in real-time with a comprehensive dashboard!

**Quick Launch:**
```bash
# Install dependencies (includes Streamlit, Plotly)
pip install -r requirements.txt

# Launch dashboard (requires API server running)
python3 launch_dashboard.py
# or
./launch_dashboard.sh

# Dashboard available at http://localhost:8501
```

**Dashboard Features:**
- 📈 **System Overview**: Uptime, query count, cache performance, response times
- 🧠 **Brain Activity**: Live neuron activity and consensus confidence trends
- 💾 **Memory Network**: Memory count, connections, and growth visualization
- ⚠️ **Health Monitoring**: API connectivity, performance indicators, and alerts
- 📊 **Interactive Charts**: Real-time Plotly visualizations with live updates
- 🔄 **Auto-refresh**: Continuous monitoring every 2 seconds

**What You Can Monitor:**
- Real-time consensus decision processes
- Memory palace network growth and connectivity
- Neuron performance and health status
- Cache hit rates and response times
- System uptime and query throughput
- Alert notifications for issues

## 🛠️ Tool Integration

Chappy can now use external tools to enhance his problem-solving capabilities!

**Automatic Tool Usage:**
Chappy automatically detects when queries require tools and uses them intelligently:
- **Mathematical queries** → Calculator tool
- **Search requests** → Web search tool  
- **Code execution** → Code execution tool
- **Knowledge queries** → Knowledge base tool

**Available Tools:**
- **🧮 Calculator**: Symbolic math, equations, and calculations using SymPy
- **🌐 Web Search**: Current information via DuckDuckGo API
- **💻 Code Execution**: Safe Python, JavaScript, and Bash execution
- **📚 Knowledge Base**: Math facts, unit conversions, structured data

**Direct Tool Access:**
```bash
# List available tools
curl http://localhost:8000/api/v1/tools

# Execute a tool directly
curl -X POST http://localhost:8000/api/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "calculator", "params": {"expression": "2**10 + sqrt(144)"}}'
```

**Safety Features:**
- Sandboxed code execution
- Input validation and sanitization
- Dangerous operation blocking
- Timeout protection
- Restricted system access

## 🎥 YouTube Learning System

Chappy can now watch and learn from educational YouTube videos!

**Features:**
- **🎬 Video Acquisition**: Downloads YouTube videos and extracts frames
- **🧠 Multimodal Processing**: Parallel vision (LLaVA), audio (Whisper), and text analysis
- **📚 Knowledge Extraction**: Uses LLM to synthesize structured knowledge from videos
- **🧠 Memory Integration**: Stores learned concepts in the Memory Palace
- **🔍 Knowledge Retrieval**: Query and recall learned video content
- **📊 Learning Statistics**: Track videos processed and knowledge extracted

**Usage Examples:**
```bash
# Teach Chappy about machine learning
"learn from video: https://youtube.com/watch?v=VIDEO_ID"

# Ask about learned topics
"what do you know about neural networks?"
"find videos about artificial intelligence"
"learning stats"
```

**Technical Details:**
- Processes videos at 1 FPS for temporal analysis
- Uses Ollama LLaVA for vision understanding
- Whisper for speech-to-text transcription
- LLM synthesis for structured knowledge extraction
- Full integration with existing brain consensus mechanisms

## 📊 Demo Output Example

```
🧠 Amygdala_Threat (confidence: 0.50)
   Response: I recommend taking caution and prioritizing safety...

🧠 Logic_Classifier (confidence: 0.50)
   Response: I would classify the object as a "Snake"...

🏆 CONSENSUS REACHED
   Winning Neuron: Amygdala_Threat
   Confidence: 0.50
   Decision: Taking caution and prioritizing safety
```

## 🎥 YouTube Learning Demo

```bash
# Run the video learning demo
python3 demo_video_learning.py

# Example output:
🎥 Chappy's YouTube Learning System Demo
==================================================
🧠 Initializing brain components...
🎬 Initializing video learning container...
✅ Video learning system ready!

💬 User: learning stats
🎯 Chappy: 📊 Video Learning Statistics:
• Videos Processed: 0
• Total Learning Time: 0.0 seconds
• Average Confidence: 0.00
• Knowledge Items Extracted: 0

💬 User: what do you know about machine learning?
🎯 Chappy: 📚 Based on my video learning:
[Chappy synthesizes knowledge from learned videos...]

🎬 To learn from a YouTube video, use:
💬 'learn from video: https://youtube.com/watch?v=VIDEO_ID'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           DIGITAL CORTEX SYSTEM                  │
├─────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐    │
│  │         DIGITAL BODY CONTAINERS         │    │
│  ├─────────────────────────────────────────┤    │
│  │  ┌─────────────┐ ┌─────────────┐        │    │
│  │  │  SENSORY    │ │   MOTOR     │        │    │
│  │  │  CONTAINER  │ │  CONTAINER  │        │    │
│  │  │             │ │             │        │    │
│  │  │ 🎥 Video    │ │ 💪 Actions  │        │    │
│  │  │ 🖼️ Vision   │ │ 🗣️ Speech   │        │    │
│  │  │ 🔊 Audio    │ │ ✋ Motor    │        │    │
│  │  └─────────────┘ └─────────────┘        │    │
│  └─────────────────────────────────────────┘    │
│         │              │                        │
│         ▼              ▼                        │
│  ┌─────────────────────────────────────────┐    │
│  │           BRAIN CONTAINER               │    │
│  ├─────────────────────────────────────────┤    │
│  │  ┌──────────────┐      ┌──────────────┐ │    │
│  │  │ LLM-Neurons  │─────▶│   Corpus     │ │    │
│  │  │  (Parallel)  │      │  Colosseum   │ │    │
│  │  └──────────────┘      │  (Consensus) │ │    │
│  │         │              └──────┬───────┘ │    │
│  │         │                     │          │    │
│  │         ▼                     ▼          │    │
│  │  ┌──────────────┐      ┌──────────────┐ │    │
│  │  │   Message    │      │   Decision   │ │    │
│  │  │   Protocol   │      │    Output    │ │    │
│  │  └──────────────┘      └──────────────┘ │    │
│  │                                           │    │
│  │  ┌──────────────┐      ┌──────────────┐ │    │
│  │  │  Memory      │      │   Frontal    │ │    │
│  │  │   Palace     │◄────►│    Lobe      │ │    │
│  │  │  (Long-term) │      │ (Executive)  │ │    │
│  │  └──────────────┘      └──────────────┘ │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │        AUTONOMIC CONTAINER              │    │
│  ├─────────────────────────────────────────┤    │
│  │  ┌──────────────┐      ┌──────────────┐ │    │
│  │  │   Amygdala   │      │    Sleep     │ │    │
│  │  │  (Emotion)   │      │   Cycle      │ │    │
│  │  └──────────────┘      └──────────────┘ │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
digital_cortex/
├── __init__.py
├── corpus_colosseum/
│   ├── __init__.py
│   ├── attention_consensus.py    # Advanced consensus mechanisms
│   └── colosseum.py              # Consensus mechanism
├── cortex_regions/
│   ├── __init__.py
│   ├── meta_cognition.py         # Self-monitoring system
│   └── frontal_lobe.py           # Executive decision making
├── learning_center/
│   ├── __init__.py
│   ├── video_acquisition.py      # YouTube video downloading
│   ├── multimodal_sensorium.py   # Vision/audio/text processing
│   ├── video_learning_orchestrator.py  # Learning coordination
│   ├── knowledge_retrieval.py    # Knowledge querying
│   └── video_learning_container.py     # Container integration
├── memory_palace/
│   ├── __init__.py
│   ├── knowledge_graph.py        # Graph-based memory
│   ├── memory_manager.py         # Memory management
│   └── palace_chain.py           # Chain-based memory
├── sensorium/
│   ├── __init__.py
│   └── sensorium.py              # Text processing
├── amygdala/
│   ├── __init__.py
│   └── amygdala.py               # Emotion processing
├── motor_cortex/
│   ├── __init__.py
│   └── executor.py               # Action execution
├── feedback/
│   ├── __init__.py
│   ├── assessor.py               # Outcome assessment
│   └── learner.py                # Weight learning
├── sleep/
│   ├── __init__.py
│   ├── consolidator.py           # Memory consolidation
│   └── dreamer.py                # Dream generation
├── utils/
│   ├── __init__.py
│   ├── message.py                # Message protocol
│   ├── llm_neuron.py             # LLM interface
│   ├── confidence_scorer.py      # Advanced confidence scoring
│   ├── async_utils.py            # Async utilities
│   ├── cache.py                  # Caching system
│   ├── config.py                 # Configuration management
│   └── model_manager.py          # Model management
├── tests/
│   ├── __init__.py
│   ├── test_*.py                 # Comprehensive test suite
│   └── __pycache__/
├── demo_integration.py           # Full system demo
├── test_neuron_quick.py          # Quick connectivity test
└── __pycache__/
```

## 🎯 What's Next (Roadmap)

### ✅ **Phase 1: Core Architecture - COMPLETE**
- [x] Message Protocol with validation and factory methods
- [x] Corpus Colosseum consensus mechanism with DBSCAN clustering
- [x] LLM-Neuron interface with confidence extraction
- [x] End-to-end integration demo

### ✅ **Phase 2: Memory Palace Chain - COMPLETE**
- [x] Sequential room creation with hash-based addressing
- [x] Chain traversal for "internal voice" simulation
- [x] Graph-based memory system for richer associations
- [x] Integration with Corpus Colosseum outputs

### ✅ **Phase 3: Feedback Cycle - COMPLETE**
- [x] Motor Cortex (action executor) for task execution
- [x] Outcome Assessment Module for performance evaluation
- [x] Weight Update Mechanism with temporal credit assignment
- [x] Learning integration across all brain regions

### ✅ **Phase 4: Sleep Cycle - COMPLETE**
- [x] Dream branch spawning with random walks
- [x] Learning branch processing and consolidation
- [x] Memory reorganization with meta-memory creation
- [x] Offline learning and memory optimization

### ✅ **Phase 5: Specialized Neural Networks - COMPLETE**
- [x] Sensorium (vision, text processing, multimodal input)
- [x] Amygdala (urgency assessment and emotional processing)
- [x] Frontal Lobe (executive function and decision making)
- [x] Meta-cognition layer for self-monitoring

### ✅ **Phase 6: Digital Body Architecture - COMPLETE**
- [x] Container Architecture with multi-container pod design
- [x] Message Bus for inter-container communication
- [x] Health Monitoring and auto-regulation systems
- [x] Complete embodied AI system integration

### ✅ **Phase 7: YouTube Learning System - COMPLETE**
- [x] Video Acquisition with YouTube downloading and frame extraction
- [x] Multimodal Sensorium (Vision/Audio/Text parallel processing)
- [x] Learning Orchestration with consensus synthesis
- [x] Knowledge Extraction and structured learning
- [x] Memory Integration with existing brain architecture
- [x] Knowledge Retrieval and querying system

### 🔄 **Phase 8: Multi-Agent Collaboration (In Progress)**
- [ ] Agent communication protocols
- [ ] Task decomposition and distribution
- [ ] Collaborative problem-solving
- [ ] Agent specialization and role assignment

## 🧪 Testing

The system has been validated with:
- ✅ Message protocol serialization/deserialization
- ✅ Corpus Colosseum consensus with mock data
- ✅ LLM-Neuron connectivity to Ollama
- ✅ End-to-end integration with real LLMs
- ✅ Snake vs Garden Hose scenario (white paper example)
- ✅ Memory Palace chain operations
- ✅ Feedback cycle weight updates
- ✅ Sleep cycle memory consolidation
- ✅ Digital Body container architecture
- ✅ YouTube Learning System multimodal processing
- ✅ Video knowledge extraction and retrieval

## 📝 Key Features

- **Local-First**: All processing happens on your machine
- **Modular**: Each component can be tested and improved independently
- **Extensible**: Easy to add new neuron types or consensus algorithms
- **Bio-Inspired**: Architecture mirrors actual brain function
- **Transparent**: Full visibility into decision-making process
- **🎥 Video Learning**: Can watch and learn from YouTube videos
- **🧠 Multimodal**: Processes vision, audio, and text simultaneously
- **📚 Knowledge Base**: Builds structured knowledge from video content
- **🏗️ Embodied AI**: Complete digital body with sensory-motor integration

## 🔬 Technical Details

### Consensus Mechanism
The Corpus Colosseum uses DBSCAN clustering to find where multiple neuron outputs converge:
1. Embed each neuron's output in vector space
2. Apply DBSCAN to find clusters
3. Score clusters by: `size × avg_confidence`
4. Select highest-scoring cluster
5. Return highest-confidence message from winning cluster

### Confidence Extraction
LLM-Neurons can extract confidence scores from model outputs:
- Pattern matching for `[CONFIDENCE: 0.XX]` tags
- Fallback to default 0.5 if not found
- Clamped to [0.0, 1.0] range

## 📚 References

- [Digital Cortex White Paper](Digital_Cortex_White_Paper.md)
- [AGI Execution Plan](agi%20whitepaper)
- [Memory Palace NN Repository](https://github.com/luckyduckcode/memory-palace-nueral-network-only)

## 🤝 Contributing

This is an active research project. The architecture is designed to be:
- Experimentally validated
- Iteratively improved
- Empirically tested

## 📄 License

See project repository for license information.

---

**Status**: Digital Body Architecture ✅ | YouTube Learning System ✅ | Multi-Agent Collaboration 🔄

**Latest Achievement**: Chappy can now watch educational YouTube videos and learn from them through sophisticated multimodal processing! 🎥🧠
