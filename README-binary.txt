# Chappy AI v1.0.0 - Standalone Desktop Application

🧠 **Welcome to Chappy AI** - A complete multimodal AGI system in a desktop app!

## 🚀 Quick Start

1. **Install Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Download required AI models**:
   ```bash
   ollama pull llama3.2:1b
   ollama pull llava:7b  # For video learning
   ```

4. **Run Chappy AI**:
   ```bash
   ./chappy-ai
   ```

## 📋 System Requirements

- Linux x64 (Ubuntu 20.04+, Fedora 30+, etc.)
- 4GB RAM minimum, 8GB recommended
- Ollama running with models loaded
- ~5GB free disk space

## 🧠 What is Chappy?

Chappy is a bio-mimetic AGI architecture inspired by biological brain systems. Unlike traditional monolithic AI models, Chappy uses specialized "neurons" (local LLMs) and "brain regions" working together in a container-based architecture.

### Key Features:
- **Multimodal Learning**: Vision, audio, and text processing
- **Memory Palace**: Graph-based knowledge storage and retrieval
- **Consensus System**: Multi-neuron decision making
- **Real-time Monitoring**: Live thought visualization
- **Container Architecture**: Multi-component brain simulation

## 🆘 Troubleshooting

**App won't start?**
- Make sure Ollama is running: `ollama serve`
- Check that models are downloaded: `ollama list`
- Ensure you have sufficient RAM (4GB+)

**GUI doesn't appear?**
- Try running from a terminal to see error messages
- Check that you're on a Linux desktop environment
- Ensure X11 or Wayland is available

## 📖 Documentation

For full documentation, source code, and development information:
https://github.com/luckyduckcode/brain-cluster-ai

## 📄 License

This software is provided as-is for research and educational purposes.

---

**Built with:** Python 3.12, CustomTkinter, PyTorch, Ollama
**Version:** 1.0.0
**Release Date:** November 30, 2025