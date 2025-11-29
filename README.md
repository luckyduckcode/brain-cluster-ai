# 🧠 Digital Cortex - Bio-Mimetic AGI System

A brain-inspired multi-agent AI architecture using local LLMs as "neurons" and specialized neural networks as "brain regions."

## 🎯 What We've Built (Phase 1 Complete!)

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

# Pull a model
ollama pull llama3.2:1b

# Start Ollama server
ollama serve
```

### Desktop App (Recommended)
```bash
# Install dependencies
pip install -r requirements.txt

# Launch Chappy Desktop App
./launch_chappy_desktop.sh  # Linux/Mac
# or
launch_chappy_desktop.bat   # Windows
```

### Web Interface
```bash
# Install dependencies
pip install -r requirements.txt

# Launch web interface
python3 launch_chappy.py
# Then open http://localhost:8501
```

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: ./venv/bin/activate

# Install dependencies
pip install -r requirements.txt
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

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           DIGITAL CORTEX SYSTEM                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐      ┌──────────────┐        │
│  │ LLM-Neurons  │─────▶│   Corpus     │        │
│  │  (Parallel)  │      │  Colosseum   │        │
│  └──────────────┘      │  (Consensus) │        │
│         │              └──────┬───────┘        │
│         │                     │                 │
│         ▼                     ▼                 │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   Message    │      │   Decision   │        │
│  │   Protocol   │      │    Output    │        │
│  └──────────────┘      └──────────────┘        │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
digital_cortex/
├── __init__.py
├── corpus_colosseum/
│   ├── __init__.py
│   └── colosseum.py          # Consensus mechanism
├── utils/
│   ├── __init__.py
│   ├── message.py             # Message protocol
│   └── llm_neuron.py          # LLM interface
├── tests/
│   └── test_colosseum.py      # Unit tests
├── demo_integration.py        # Full system demo
└── test_neuron_quick.py       # Quick connectivity test
```

## 🎯 What's Next (Roadmap)

### Phase 2: Memory Palace Chain
- [x] Sequential room creation
- [x] Hash-based addressing
- [x] Chain traversal for "internal voice"
- [x] Integration with Corpus Colosseum outputs

### Phase 3: Feedback Cycle
- [x] Motor Cortex (action executor)
- [x] Outcome Assessment Module
- [x] Weight Update Mechanism
- [x] Temporal credit assignment

### Phase 4: Sleep Cycle
- [x] Dream branch spawning (Random Walks)
- [x] Learning branch processing (Consolidation)
- [x] Memory reorganization (Meta-memory creation)

### Phase 5: Specialized NNs
- [x] Sensorium (vision, text processing)
- [x] Amygdala (urgency assessment)
- [ ] Frontal Lobe (executive function)

## 🧪 Testing

The system has been validated with:
- ✅ Message protocol serialization/deserialization
- ✅ Corpus Colosseum consensus with mock data
- ✅ LLM-Neuron connectivity to Ollama
- ✅ End-to-end integration with real LLMs
- ✅ Snake vs Garden Hose scenario (white paper example)

## 📝 Key Features

- **Local-First**: All processing happens on your machine
- **Modular**: Each component can be tested and improved independently
- **Extensible**: Easy to add new neuron types or consensus algorithms
- **Bio-Inspired**: Architecture mirrors actual brain function
- **Transparent**: Full visibility into decision-making process

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

**Status**: Phase 1 Complete ✅ | Next: Memory Palace Chain Integration
