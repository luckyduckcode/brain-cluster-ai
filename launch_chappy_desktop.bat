@echo off
REM Chappy Desktop App Launcher (Windows)

echo 🧠 Starting Chappy Desktop Application...
echo Make sure Ollama is running: 'ollama serve'
echo And you have the model: 'ollama pull llama3.2:1b'
echo.

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Activate virtual environment
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM Run the desktop app
python "%SCRIPT_DIR%chappy_desktop.py"

echo 👋 Chappy desktop app closed.
pause