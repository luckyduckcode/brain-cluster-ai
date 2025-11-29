"""Test the Feedback Cycle."""

import sys
import os
import shutil
import tempfile
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.motor_cortex import MotorCortex, Action
from digital_cortex.feedback import OutcomeAssessor, WeightLearner


def test_temporal_credit_assignment():
    """Test updating multiple contributing neurons."""
    print("=" * 60)
    print("Testing Temporal Credit Assignment")
    print("=" * 60)

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        learner = WeightLearner(storage_path=temp_path)

        # Simulate a winning cluster with multiple neurons
        contributing_neurons = ["Amygdala", "Logic_Agent", "Threat_Detector"]

        # Positive outcome - all should get rewarded
        learner.update_contributing_neurons(contributing_neurons, 0.8)

        for neuron in contributing_neurons:
            weight = learner.get_weight(neuron)
            assert weight == 1.08, f"Expected 1.08 for {neuron}, got {weight}"

        # Negative outcome - all should get penalized
        learner.update_contributing_neurons(contributing_neurons, -0.4)

        for neuron in contributing_neurons:
            weight = learner.get_weight(neuron)
            assert weight == 1.04, f"Expected 1.04 for {neuron}, got {weight}"

        print("✓ Temporal credit assignment test passed!")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_weight_clamping():
    """Test that weights are properly clamped."""
    print("\n" + "=" * 60)
    print("Testing Weight Clamping")
    print("=" * 60)

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        learner = WeightLearner(storage_path=temp_path)

        # Test upper bound
        learner.update("Test_Neuron", 10.0)  # Should clamp to 2.0
        assert learner.get_weight("Test_Neuron") == 2.0, f"Expected 2.0, got {learner.get_weight('Test_Neuron')}"

        # Test lower bound (from upper bound, should go down but not below 0.1)
        learner.update("Test_Neuron", -10.0)  # 2.0 + (0.1 * -10.0) = 1.0, which is within bounds
        assert learner.get_weight("Test_Neuron") == 1.0, f"Expected 1.0, got {learner.get_weight('Test_Neuron')}"
        
        # Now test actual clamping to lower bound
        learner.update("Test_Neuron", -20.0)  # Should clamp to 0.1
        assert learner.get_weight("Test_Neuron") == 0.1, f"Expected 0.1, got {learner.get_weight('Test_Neuron')}"

        print("✓ Weight clamping test passed!")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_feedback_cycle():
    """Test the complete feedback loop."""
    print("=" * 60)
    print("Testing Feedback Cycle")
    print("=" * 60)
    
    # Setup
    sandbox_dir = "./test_sandbox"
    if os.path.exists(sandbox_dir):
        shutil.rmtree(sandbox_dir)
    
    # 1. Initialize components
    motor = MotorCortex(sandbox_dir=sandbox_dir)
    assessor = OutcomeAssessor()
    learner = WeightLearner(storage_path="test_weights.json")
    
    print("✓ Initialized components")
    
    # 2. Define an action (e.g., write a file)
    action = Action(
        type="write_file",
        params={"path": "test.txt", "content": "Hello World"},
        source="Writer_Neuron"
    )
    print(f"\n[Action] {action.type} by {action.source}")
    
    # 3. Execute Action
    outcome = motor.execute(action)
    print(f"[Result] Status: {outcome['result']['status']}")
    
    # 4. Assess Outcome
    assessment = assessor.assess(
        action.type, 
        action.params, 
        outcome['result']
    )
    print(f"[Assessment] Success: {assessment.success}, Score: {assessment.score}")
    
    # 5. Update Weights
    print(f"\n[Learning] Updating weights for {action.source}...")
    old_weight = learner.get_weight(action.source)
    learner.update(action.source, assessment.score)
    new_weight = learner.get_weight(action.source)
    
    print(f"  Weight changed: {old_weight:.2f} -> {new_weight:.2f}")
    
    if new_weight > old_weight:
        print("✓ Weight increased after success")
    else:
        print("❌ Weight did not increase")
        
    # Cleanup
    if os.path.exists(sandbox_dir):
        shutil.rmtree(sandbox_dir)
    if os.path.exists("test_weights.json"):
        os.remove("test_weights.json")
        
    print("\n" + "=" * 60)
    print("✓ Feedback Cycle test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_temporal_credit_assignment()
    test_weight_clamping()
    test_feedback_cycle()
