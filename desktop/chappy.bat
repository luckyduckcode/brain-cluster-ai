@echo off
REM Chappy Desktop App Launcher (Windows)

echo 🧠 Starting Chappy Desktop Application...
echo Make sure Ollama is running: 'ollama serve'
echo And you have the model: 'ollama pull llama3.2:1b'
echo.

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..\..

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Run the desktop app launcher
python "%SCRIPT_DIR%..\launchers\desktop_app.py"

echo 👋 Chappy desktop app closed.
pause