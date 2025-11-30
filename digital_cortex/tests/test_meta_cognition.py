import unittest
from digital_cortex.cortex_regions.meta_cognition import MetaCognitionLayer

class TestMetaCognition(unittest.TestCase):
    def setUp(self):
        self.meta = MetaCognitionLayer()

    def test_monitor_consensus_normal(self):
        # Normal consensus: clear winner, high confidence
        metadata = {
            "cluster_count": 2,
            "total_messages": 5,
            "winning_cluster_avg_confidence": 0.9,
            "selection": "cluster_consensus"
        }
        state = self.meta.monitor_consensus(metadata)
        
        self.assertFalse(state.is_stuck)
        self.assertFalse(state.needs_clarification)
        self.assertTrue(state.uncertainty_level < 0.2)

    def test_monitor_consensus_stuck(self):
        # Stuck: many clusters (fragmented), low confidence
        metadata = {
            "cluster_count": 5,
            "total_messages": 5,
            "winning_cluster_avg_confidence": 0.3,
            "selection": "highest_confidence_fallback"
        }
        state = self.meta.monitor_consensus(metadata)
        
        self.assertTrue(state.is_stuck)
        self.assertTrue(state.confusion_level > 0.8)

    def test_calibration_check(self):
        # Overconfident failure
        self.meta.check_calibration(0.9, -1.0) # Confident (0.9) but failed (-1.0 -> 0.0)
        
        status = self.meta.get_status()
        self.assertEqual(status["calibration_alerts"], 1)
        self.assertEqual(self.meta.calibration_errors[0]["type"], "overconfident")

if __name__ == '__main__':
    unittest.main()
