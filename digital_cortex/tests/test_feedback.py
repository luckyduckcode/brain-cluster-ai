"""Test the Feedback Cycle."""

import sys
import os
import shutil
sys.path.insert(0, '/home/duck/Documents/brain cluster ai')

from digital_cortex.motor_cortex import MotorCortex, Action
from digital_cortex.feedback import OutcomeAssessor, WeightLearner

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
    test_feedback_cycle()
