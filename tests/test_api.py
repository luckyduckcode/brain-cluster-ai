#!/usr/bin/env python3
"""
Test Chappy API

Basic tests for the REST API endpoints.
"""

import requests
import time
import json
from typing import Dict, Any

def test_api_status():
    """Test the status endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        print("✅ Status endpoint working")
        print(f"   Status: {data['status']}")
        print(f"   Neurons: {data['neuron_count']}")
        print(f"   Memories: {data['memory_count']}")
        return True
    except Exception as e:
        print(f"❌ Status endpoint failed: {e}")
        return False

def test_api_query():
    """Test the query endpoint."""
    try:
        payload = {
            "query": "Hello, how are you?",
            "max_memories": 3,
            "include_thoughts": False
        }
        response = requests.post("http://localhost:8000/api/v1/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        print("✅ Query endpoint working")
        print(f"   Response: {data['response'][:100]}...")
        print(f"   Confidence: {data['confidence']:.2f}")
        print(f"   Processing time: {data['processing_time']:.2f}s")
        print(f"   Consensus: {data['consensus_reached']}")
        return True
    except Exception as e:
        print(f"❌ Query endpoint failed: {e}")
        return False

def test_api_memories():
    """Test the memories endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/v1/memories?limit=5")
        assert response.status_code == 200
        data = response.json()
        print("✅ Memories endpoint working")
        print(f"   Retrieved {len(data['memories'])} memories")
        return True
    except Exception as e:
        print(f"❌ Memories endpoint failed: {e}")
        return False

def test_api_feedback():
    """Test the feedback endpoint."""
    try:
        payload = {
            "query": "Test query",
            "response": "Test response",
            "rating": 0.8,
            "feedback_text": "Good response"
        }
        response = requests.post("http://localhost:8000/api/v1/feedback", json=payload)
        assert response.status_code == 200
        data = response.json()
        print("✅ Feedback endpoint working")
        print(f"   Message: {data['message']}")
        return True
    except Exception as e:
        print(f"❌ Feedback endpoint failed: {e}")
        return False

def wait_for_api_ready(max_wait: int = 30):
    """Wait for API to be ready."""
    print("⏳ Waiting for API to start...")
    for i in range(max_wait):
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ API failed to start within timeout")
    return False

def main():
    """Run all API tests."""
    print("🧪 Testing Chappy API")
    print("=" * 50)

    # Wait for API to be ready
    if not wait_for_api_ready():
        return False

    # Run tests
    tests = [
        test_api_status,
        test_api_query,
        test_api_memories,
        test_api_feedback
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All API tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)