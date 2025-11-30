#!/bin/bash
# Launcher script for Brain Cluster AI Observability Dashboard
# Starts the Streamlit dashboard for real-time system monitoring

echo "🧠 Starting Brain Cluster AI Observability Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:8501"
echo "🔗 Make sure the API server is running on http://localhost:8000"
echo "Press Ctrl+C to stop the dashboard"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Launch the dashboard
python3 -m streamlit run observability_dashboard.py --server.port 8501 --server.address 0.0.0.0