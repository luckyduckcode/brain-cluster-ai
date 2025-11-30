#!/usr/bin/env python3
"""
Test script for Chappy Standalone Desktop App

Tests the basic functionality without requiring a display.
"""

import sys
import os
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from chappy_standalone import ChappyDesktopApp
        print("✓ ChappyDesktopApp imported successfully")

        from chappy_gui import ChappyBrainGUI
        print("✓ ChappyBrainGUI imported successfully")

        import customtkinter as ctk
        print("✓ CustomTkinter available")

        import darkdetect
        print("✓ Darkdetect available")

        import yt_dlp
        print("✓ yt-dlp available")

        import cv2
        print("✓ OpenCV available")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_brain_initialization():
    """Test brain initialization without GUI."""
    try:
        from chappy_gui import ChappyBrainGUI
        brain = ChappyBrainGUI()
        print("✓ ChappyBrainGUI instance created")

        # Test basic attributes
        assert hasattr(brain, 'neuron_pool')
        assert hasattr(brain, 'memory_palace')
        assert hasattr(brain, 'colosseum')
        print("✓ Brain components initialized")

        return True
    except Exception as e:
        print(f"✗ Brain initialization error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧠 Testing Chappy Standalone Desktop App")
    print("=" * 50)

    tests_passed = 0
    total_tests = 2

    if test_imports():
        tests_passed += 1

    if test_brain_initialization():
        tests_passed += 1

    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 All tests passed! The standalone app is ready.")
        print("\nTo run the app:")
        print("  python3 launch_chappy_standalone.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())