import unittest
from unittest.mock import MagicMock
from digital_cortex.corpus_colosseum.attention_consensus import AttentionVoter, HierarchicalConsensus
from digital_cortex.utils.message import Message

class TestAttentionVoter(unittest.TestCase):
    def setUp(self):
        self.voter = AttentionVoter()
        self.messages = [
            Message.create("neuron1", "answer A", 0.9),
            Message.create("neuron2", "answer A", 0.8),
            Message.create("neuron3", "answer B", 0.7)
        ]

    def test_compute_attention_scores(self):
        scores = self.voter.compute_attention_scores(self.messages)
        
        # Should have scores for all neurons
        self.assertEqual(len(scores), 3)
        
        # Scores should sum to 1.0 (normalized)
        self.assertAlmostEqual(sum(scores.values()), 1.0, places=5)

    def test_weighted_vote(self):
        scores = self.voter.compute_attention_scores(self.messages)
        winner, metadata = self.voter.weighted_vote(self.messages, scores)
        
        # Winner should be from the group with higher combined weight
        # neuron1 + neuron2 both say "answer A"
        self.assertIn(winner.source, ["neuron1", "neuron2"])
        self.assertEqual(metadata["method"], "attention_weighted_vote")

    def test_update_weights(self):
        initial_weight = self.voter.neuron_weights["neuron1"]
        
        # Positive performance
        self.voter.update_weights("neuron1", 0.5)
        new_weight = self.voter.neuron_weights["neuron1"]
        
        self.assertGreater(new_weight, initial_weight)

class TestHierarchicalConsensus(unittest.TestCase):
    def setUp(self):
        self.hierarchical = HierarchicalConsensus()
        self.messages = [
            Message.create("n1", "answer", 0.9),
            Message.create("n2", "answer", 0.85)
        ]

    def test_fast_decision_high_urgency(self):
        context = {"urgency": 0.9}
        result = self.hierarchical.decide(self.messages, context)
        
        self.assertEqual(result["level"], "fast")
        self.assertIsNotNone(result["decision"])

    def test_fast_decision_high_confidence(self):
        result = self.hierarchical.decide(self.messages)
        
        # Average confidence is 0.875, above fast threshold (0.7)
        self.assertEqual(result["level"], "fast")

    def test_uncertain_decision(self):
        low_conf_messages = [
            Message.create("n1", "answer", 0.3),
            Message.create("n2", "answer", 0.4)
        ]
        result = self.hierarchical.decide(low_conf_messages)
        
        self.assertEqual(result["level"], "uncertain")

if __name__ == '__main__':
    unittest.main()
