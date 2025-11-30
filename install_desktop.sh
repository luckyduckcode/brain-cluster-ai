#!/bin/bash
# Chappy AI Desktop Integration Installer

echo "🖥️  Installing Chappy AI Desktop Integration..."

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is for Linux systems only."
    echo "For Windows, manually create a shortcut to desktop/chappy.bat"
    exit 1
fi

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create applications directory if it doesn't exist
mkdir -p ~/.local/share/applications

# Copy desktop file
cp "$PROJECT_DIR/desktop/chappy.desktop" ~/.local/share/applications/

# Update the Exec path in the desktop file
sed -i "s|Exec=.*|Exec=$PROJECT_DIR/launchers/desktop_app.py|" ~/.local/share/applications/chappy.desktop

# Update the Icon path
sed -i "s|Icon=.*|Icon=$PROJECT_DIR/desktop/icons/chappy_icon.png|" ~/.local/share/applications/chappy.desktop

# Make launchers executable
chmod +x "$PROJECT_DIR/launchers/"*.py

echo "✅ Desktop integration installed!"
echo "You should now see 'Chappy AI' in your applications menu."
echo ""
echo "To launch Chappy:"
echo "  - Click the Chappy AI icon in your applications menu"
echo "  - Or run: python3 $PROJECT_DIR/launchers/main_launcher.py"
echo ""
echo "Make sure Ollama is running: ollama serve"