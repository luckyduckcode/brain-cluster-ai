"""Test the Sensorium sensory processing system."""

import sys
import os
import tempfile
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.sensorium import Sensorium
from digital_cortex.utils.message import Message


def test_sensorium_text_processing():
    """Test text input processing."""
    print("=" * 60)
    print("Testing Sensorium - Text Processing")
    print("=" * 60)

    sensorium = Sensorium()

    # Test basic text processing
    test_text = "This is a test message for the Sensorium. It contains multiple sentences and should be analyzed properly."
    message = sensorium.process_text(test_text, source="test_input")

    print(f"✓ Processed text: {message.content[:80]}...")
    print(f"  Source: {message.source}")
    print(f"  Confidence: {message.confidence:.2f}")

    # Check metadata
    assert "sensorium_type" in message.metadata
    assert message.metadata["sensorium_type"] == "text"
    assert "text_analysis" in message.metadata

    text_analysis = message.metadata["text_analysis"]
    assert text_analysis["word_count"] > 0
    assert text_analysis["sentence_count"] > 0

    print("✓ Text analysis metadata present")
    print(f"  Word count: {text_analysis['word_count']}")
    print(f"  Sentence count: {text_analysis['sentence_count']}")

    print("✓ Text processing test passed!")


def test_sensorium_image_processing():
    """Test image input processing."""
    print("\n" + "=" * 60)
    print("Testing Sensorium - Image Processing")
    print("=" * 60)

    sensorium = Sensorium()

    # Create a simple test image
    from PIL import Image
    import numpy as np

    # Create a simple RGB image
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, 'RGB')

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_path = tmp_file.name
        img.save(tmp_path)

    try:
        # Process the image
        message = sensorium.process_image(tmp_path, source="test_image")

        print(f"✓ Processed image: {message.content[:80]}...")
        print(f"  Source: {message.source}")
        print(f"  Confidence: {message.confidence:.2f}")

        # Check metadata
        assert "sensorium_type" in message.metadata
        assert message.metadata["sensorium_type"] == "image"
        assert "image_analysis" in message.metadata

        image_analysis = message.metadata["image_analysis"]
        assert "dimensions" in image_analysis
        assert image_analysis["dimensions"] == (100, 100)

        print("✓ Image analysis metadata present")
        print(f"  Dimensions: {image_analysis['dimensions']}")
        print(f"  Mode: {image_analysis.get('mode', 'N/A')}")

        print("✓ Image processing test passed!")

    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_sensorium_environment_capture():
    """Test environment state capture."""
    print("\n" + "=" * 60)
    print("Testing Sensorium - Environment Capture")
    print("=" * 60)

    sensorium = Sensorium()

    # Test environment capture
    message = sensorium.capture_environment_state(context="test_context")

    print(f"✓ Captured environment: {message.content[:80]}...")
    print(f"  Source: {message.source}")
    print(f"  Confidence: {message.confidence:.2f}")

    # Check metadata
    assert "sensorium_type" in message.metadata
    assert message.metadata["sensorium_type"] == "environment"
    assert "environment_info" in message.metadata

    env_info = message.metadata["environment_info"]
    assert "os" in env_info
    assert "cpu_count" in env_info

    print("✓ Environment info captured")
    print(f"  OS: {env_info['os']}")
    print(f"  CPU Count: {env_info['cpu_count']}")

    print("✓ Environment capture test passed!")


def test_sensorium_integration():
    """Test Sensorium integration with message system."""
    print("\n" + "=" * 60)
    print("Testing Sensorium - Message Integration")
    print("=" * 60)

    sensorium = Sensorium()

    # Process different types of inputs
    messages = []

    # Text input
    text_msg = sensorium.process_text("Hello world!", source="integration_test")
    messages.append(text_msg)

    # Environment capture
    env_msg = sensorium.capture_environment_state(context="integration")
    messages.append(env_msg)

    print(f"✓ Generated {len(messages)} messages")

    # Verify all messages are proper Message objects
    for i, msg in enumerate(messages):
        assert isinstance(msg, Message)
        assert hasattr(msg, 'source')
        assert hasattr(msg, 'content')
        assert hasattr(msg, 'confidence')
        assert hasattr(msg, 'timestamp')
        print(f"  Message {i+1}: {msg.source} - confidence {msg.confidence:.2f}")

    print("✓ All messages are valid Message objects")
    print("✓ Message integration test passed!")


if __name__ == "__main__":
    test_sensorium_text_processing()
    test_sensorium_image_processing()
    test_sensorium_environment_capture()
    test_sensorium_integration()

    print("\n" + "=" * 60)
    print("🎉 All Sensorium tests passed!")
    print("=" * 60)