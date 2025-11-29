"""Test the Amygdala threat assessment system."""

import sys
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.amygdala import Amygdala, ThreatAssessment
from digital_cortex.utils.message import Message


def test_amygdala_threat_assessment():
    """Test threat assessment capabilities."""
    print("=" * 60)
    print("Testing Amygdala - Threat Assessment")
    print("=" * 60)

    amygdala = Amygdala()

    # Test cases with different threat levels
    test_cases = [
        {
            "text": "Everything is normal and safe here.",
            "expected_threat": 0.0,
            "expected_urgency": 0.0,
            "description": "Safe scenario"
        },
        {
            "text": "I see something suspicious that might be a threat.",
            "expected_threat": 0.6,  # "threat" keyword
            "expected_urgency": 0.0,
            "description": "Medium threat"
        },
        {
            "text": "DANGER! There's a deadly snake that could kill us immediately!",
            "expected_threat": 0.9,  # "danger", "deadly", "kill"
            "expected_urgency": 0.8,  # "immediately"
            "description": "High threat with urgency"
        },
        {
            "text": "What is that coiled object? Should I be careful?",
            "expected_threat": 0.3,  # "careful"
            "expected_urgency": 0.3,  # question indicates uncertainty
            "description": "Question with caution"
        }
    ]

    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['description']}")
        print(f"Text: {test_case['text'][:60]}...")

        assessment = amygdala.assess_threat(test_case['text'])

        print(f"Threat: {assessment.threat_level:.2f} (expected: {test_case['expected_threat']:.1f})")
        print(f"Urgency: {assessment.urgency:.2f} (expected: {test_case['expected_urgency']:.1f})")
        print(f"Valence: {assessment.valence:.2f}")
        print(f"Confidence: {assessment.confidence:.2f}")
        print(f"Triggers: {assessment.triggers[:3]}...")  # Show first 3
        print(f"Reasoning: {assessment.reasoning}")

        # Basic validation
        assert isinstance(assessment, ThreatAssessment)
        assert 0.0 <= assessment.threat_level <= 1.0
        assert 0.0 <= assessment.urgency <= 1.0
        assert -1.0 <= assessment.valence <= 1.0
        assert 0.0 <= assessment.confidence <= 1.0

        print("✓ Assessment structure valid")

    print("\n✓ Threat assessment tests passed!")


def test_amygdala_message_processing():
    """Test message processing through Amygdala."""
    print("\n" + "=" * 60)
    print("Testing Amygdala - Message Processing")
    print("=" * 60)

    amygdala = Amygdala()

    # Create test messages
    test_messages = [
        Message.create("Sensorium", "A coiled green object detected", 0.6),
        Message.create("Logic", "This appears to be a garden hose", 0.7),
        Message.create("Threat_Detector", "POTENTIAL DANGER: Unknown object could be deadly", 0.8)
    ]

    for i, msg in enumerate(test_messages):
        print(f"\nProcessing message {i+1}: {msg.source}")
        print(f"Original: {msg.content[:50]}...")

        processed_msg = amygdala.process_message(msg)

        print(f"Processed: {processed_msg.content[:80]}...")
        print(f"Source: {processed_msg.source}")
        print(f"Confidence: {msg.confidence:.2f} -> {processed_msg.confidence:.2f}")

        # Check that Amygdala assessment was added to metadata
        assert "amygdala_assessment" in processed_msg.metadata
        assessment = processed_msg.metadata["amygdala_assessment"]

        assert "threat_level" in assessment
        assert "urgency" in assessment
        assert "valence" in assessment
        assert "confidence" in assessment

        print(f"Amygdala threat level: {assessment['threat_level']:.2f}")
        print("✓ Message processing successful")

    print("\n✓ Message processing tests passed!")


def test_amygdala_valence_assessment():
    """Test emotional valence assessment."""
    print("\n" + "=" * 60)
    print("Testing Amygdala - Valence Assessment")
    print("=" * 60)

    amygdala = Amygdala()

    # Test positive and negative valence
    valence_tests = [
        ("This is wonderful and makes me happy!", 0.4, "Positive emotion"),
        ("This is terrible and makes me sad.", -0.4, "Negative emotion"),
        ("DANGER! Deadly threat approaching!", -0.9, "Threat reduces valence"),
        ("Everything is calm and peaceful.", 0.4, "Positive calm")
    ]

    for text, expected_min, description in valence_tests:
        assessment = amygdala.assess_threat(text)
        print(f"{description}: '{text[:30]}...' -> valence {assessment.valence:.2f}")

        if "Positive" in description:
            assert assessment.valence > 0, f"Expected positive valence for: {text}"
        elif "Negative" in description or "Threat" in description:
            assert assessment.valence < 0, f"Expected negative valence for: {text}"

    print("✓ Valence assessment tests passed!")


def test_amygdala_integration():
    """Test Amygdala integration with overall system."""
    print("\n" + "=" * 60)
    print("Testing Amygdala - System Integration")
    print("=" * 60)

    amygdala = Amygdala()

    # Test emotional state
    state = amygdala.get_emotional_state()
    assert isinstance(state, dict)
    assert "current_state" in state
    print(f"Emotional state: {state}")

    # Test state reset
    amygdala.reset_state()
    print("✓ State reset successful")

    # Test that assessments are consistent
    text = "Warning: potential threat detected!"
    assessment1 = amygdala.assess_threat(text)
    assessment2 = amygdala.assess_threat(text)

    assert assessment1.threat_level == assessment2.threat_level
    assert assessment1.urgency == assessment2.urgency
    print("✓ Assessment consistency verified")

    print("✓ System integration tests passed!")


if __name__ == "__main__":
    test_amygdala_threat_assessment()
    test_amygdala_message_processing()
    test_amygdala_valence_assessment()
    test_amygdala_integration()

    print("\n" + "=" * 60)
    print("🎉 All Amygdala tests passed!")
    print("=" * 60)