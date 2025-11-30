# Chappy AI - Brain-Inspired AI Companion

🧠 **Chappy AI** is your friendly AI companion with a brain inspired by biology. Experience natural conversations, learning, and memory capabilities.

## Features

- 🖥️ **Desktop App**: Native desktop application with modern UI
- 🧠 **Biological Brain**: Multi-region brain architecture (cortex, amygdala, etc.)
- 💭 **Memory System**: Persistent RAG memory with ChromaDB
- 🌐 **API Server**: REST API for integrations
- 📊 **Observability**: Real-time monitoring dashboard
- 🎥 **Video Learning**: Learn from YouTube videos and content
- 🔍 **Web Search**: Integrated web search capabilities

## Quick Start

### Option 1: Version Selector (Recommended)
```bash
python launchers/main_launcher.py
```
This opens a GUI where you can select which version of Chappy to run.

### Option 2: Direct Launch
```bash
# Desktop App
python launchers/desktop_app.py

# API Server
python launchers/api_server.py

# Dashboard
python launchers/dashboard.py
```

## Requirements

- Python 3.12+
- Ollama (with llama3.2:1b model)
- See `config/requirements.txt` for full dependencies

## Installation

1. **Install Ollama**:
   ```bash
   # Linux/Mac
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull the model
   ollama pull llama3.2:1b
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Desktop Integration** (Linux):
   ```bash
   # Copy desktop file
   cp desktop/chappy.desktop ~/.local/share/applications/

   # Make launchers executable
   chmod +x launchers/*.py
   ```

## Project Structure

```
├── versions/          # Version history
│   ├── v0.8.0/
│   ├── v4.8.0/
│   ├── v5.0.0/
│   ├── v5.2.0/
│   └── v2023.11.0/
├── launchers/         # Centralized launch system
│   ├── main_launcher.py    # Version selector GUI
│   ├── desktop_app.py      # Desktop app launcher
│   ├── api_server.py       # API server launcher
│   └── dashboard.py         # Dashboard launcher
├── desktop/           # Desktop integration files
│   ├── chappy.desktop       # Linux desktop file
│   ├── chappy.bat           # Windows launcher
│   └── icons/
│       └── chappy_icon.png  # App icon
├── core/              # Core application code
│   ├── chappy_standalone_simple.py
│   ├── api.py
│   └── observability_dashboard.py
├── config/            # Configuration files
│   ├── config.yaml
│   └── requirements.txt
├── docs/              # Documentation
│   ├── README.md
│   ├── PROGRESS.md
│   └── RELEASE_NOTES.md
├── data/              # Memory and data files
│   ├── chappy_memory/
│   └── chappy_weights.json
└── digital_cortex/    # Brain architecture
```

## Version History

- **v5.2.0**: Latest stable release with RAG memory system
- **v5.0.0**: Major memory system improvements
- **v4.8.0**: API server enhancements
- **v0.8.0**: Initial release

## Contributing

Found a bug or want to contribute? Check out our [progress document](docs/PROGRESS.md) and feel free to open issues or pull requests.

## License

This project is open source. See individual files for licensing information.
