#!/usr/bin/env python3
"""
Sensory Service for Chappy's Digital Body

Containerized sensory input processing service.
"""

import sys
import os
sys.path.insert(0, '/app')

from flask import Flask, jsonify, request
import json
import time
from datetime import datetime

# Import sensory system
from sensory import SensorySystem

app = Flask(__name__)
sensory_system = None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'sensory',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status', methods=['GET'])
def status():
    """Get sensory system status."""
    if sensory_system:
        return jsonify({
            'active': True,
            'sensors': sensory_system.get_sensor_status(),
            'timestamp': datetime.now().isoformat()
        })
    return jsonify({'active': False, 'error': 'Sensory system not initialized'})

@app.route('/data', methods=['GET'])
def get_data():
    """Get available sensory data."""
    if sensory_system:
        data = sensory_system.get_sensory_data()
        return jsonify({
            'data': [msg.to_dict() for msgs in data.values() for msg in msgs],
            'timestamp': datetime.now().isoformat()
        })
    return jsonify({'error': 'Sensory system not available'})

@app.route('/text', methods=['POST'])
def receive_text():
    """Receive text input."""
    if sensory_system and request.is_json:
        data = request.get_json()
        text = data.get('text', '')
        source = data.get('source', 'api')

        sensory_system.receive_text_input(text, source)

        return jsonify({
            'status': 'received',
            'text_length': len(text),
            'timestamp': datetime.now().isoformat()
        })

    return jsonify({'error': 'Invalid request'}), 400

def main():
    """Main service function."""
    global sensory_system

    print("Starting Chappy Sensory Service...")

    # Initialize sensory system
    sensory_system = SensorySystem()
    if sensory_system.initialize_sensors():
        print("✅ Sensory system initialized")

        # Start processing threads
        sensory_system.start_sensory_processing()
        print("✅ Sensory processing started")

        # Start Flask app
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        print("❌ Failed to initialize sensory system")
        sys.exit(1)

if __name__ == '__main__':
    main()