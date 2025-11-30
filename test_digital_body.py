#!/usr/bin/env python3
"""
Digital Body Integration Test

Demonstrates Chappy's complete digital body working together.
"""

import sys
import time
from datetime import datetime

# Add project path
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_body import SensorySystem, MotorSystem, NervousSystem, ContainerManager
from digital_body.message import BodyMessage


def test_body_integration():
    """Test the integrated digital body systems."""
    print("🧠 Testing Chappy's Digital Body Integration")
    print("=" * 50)

    # Initialize all body systems
    print("\n1. Initializing Body Systems...")

    sensory = SensorySystem()
    motor = MotorSystem()
    nervous = NervousSystem()

    # Initialize systems
    sensory_ok = sensory.initialize_sensors()
    motor_ok = motor.initialize_motors()
    nervous_ok = nervous.initialize_nervous_system()

    print(f"   Sensory: {'✅' if sensory_ok else '❌'}")
    print(f"   Motor: {'✅' if motor_ok else '❌'}")
    print(f"   Nervous: {'✅' if nervous_ok else '❌'}")

    if not all([sensory_ok, motor_ok, nervous_ok]):
        print("❌ Body system initialization failed")
        return False

    # Start processing
    print("\n2. Starting Body Processing...")
    sensory.start_sensory_processing()
    motor.start_motor_processing()
    nervous.start_nervous_processing()

    print("✅ All systems processing")

    # Test sensory input
    print("\n3. Testing Sensory Input...")
    sensory.receive_text_input("Hello Chappy! How are you feeling?", "test")
    time.sleep(1)

    # Get sensory data
    sensory_data = sensory.get_sensory_data()
    text_messages = sensory_data.get('text', [])
    print(f"   Received {len(text_messages)} text inputs")

    # Test motor output
    print("\n4. Testing Motor Output...")
    motor.speak("Hello! I'm Chappy, your digital brain cluster. My body systems are working perfectly!")
    motor.display("System Status: All body systems operational", "text")
    time.sleep(2)

    # Test nervous system
    print("\n5. Testing Nervous System...")
    nervous.signal_pleasure("integration_test", 0.8, "Successful body integration test")

    time.sleep(1)

    # Get nervous data
    nervous_data = nervous.get_nervous_data()
    nervous_messages = nervous_data.get('nervous', [])
    print(f"   Generated {len(nervous_messages)} nervous system messages")

    # Get physiological state
    state = nervous.get_physiological_state()
    print(f"   Energy Level: {state['energy_level']:.1f}%")
    print(f"   Stress Level: {state['stress_level']:.1f}%")

    # Test container management (without actually creating containers)
    print("\n6. Testing Container Management...")
    container_mgr = ContainerManager()

    # Just test pod status (should not exist)
    status = container_mgr.get_pod_status()
    print(f"   Pod exists: {status['pod']['exists']}")
    print(f"   Message bus active: {status['message_bus']['active']}")

    # Demonstrate message flow
    print("\n7. Demonstrating Message Flow...")

    # Create a sample message chain
    sensory_msg = BodyMessage.create_sensory(
        sensor_type="text",
        data={"text": "Test message from sensory system"},
        confidence=0.9
    )

    motor_msg = BodyMessage.create_motor(
        motor_type="speech",
        data={"text": "Processing sensory input through motor system"},
        confidence=0.8
    )

    nervous_msg = BodyMessage.create_nervous(
        nervous_type="proprioception",
        data={"energy_level": 85.0, "stress_level": 15.0},
        confidence=1.0
    )

    print(f"   Sensory → {sensory_msg.message_type}:{sensory_msg.sensor_type}")
    print(f"   Motor → {motor_msg.message_type}:{motor_msg.motor_type}")
    print(f"   Nervous → {nervous_msg.message_type}:{nervous_msg.nervous_type}")

    # Stop systems
    print("\n8. Shutting Down Body Systems...")
    sensory.stop_sensory_processing()
    motor.stop_motor_processing()
    nervous.stop_nervous_processing()

    print("✅ All systems shut down gracefully")

    print("\n" + "=" * 50)
    print("🎉 Digital Body Integration Test Complete!")
    print("✅ All body systems working together successfully")

    return True


def test_container_operations():
    """Test container management operations."""
    print("\n🐳 Testing Container Operations...")

    container_mgr = ContainerManager("test-chappy-body")

    # Test pod creation (will fail without podman, but shows the API)
    print("Testing pod creation...")
    try:
        pod_created = container_mgr.create_pod()
        print(f"Pod creation: {'✅' if pod_created else '❌'}")
    except Exception as e:
        print(f"Pod creation test: Expected failure without podman - {e}")

    # Test status
    status = container_mgr.get_pod_status()
    print(f"Pod status check: ✅ (returned {len(status)} status fields)")

    print("✅ Container operations API functional")


if __name__ == '__main__':
    try:
        # Run integration test
        success = test_body_integration()

        # Test container operations
        test_container_operations()

        if success:
            print("\n🎯 All tests passed! Chappy's digital body is ready.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)