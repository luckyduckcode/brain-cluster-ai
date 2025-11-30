import unittest
from digital_cortex.utils.confidence_scorer import ConfidenceScorer

class TestConfidenceScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = ConfidenceScorer()

    def test_explicit_confidence(self):
        text = "I am sure about this. [CONFIDENCE: 0.95]"
        score = self.scorer.score(text)
        self.assertEqual(score, 0.95)

    def test_explicit_confidence_case_insensitive(self):
        text = "This is the answer. Confidence: 0.8"
        score = self.scorer.score(text)
        self.assertEqual(score, 0.8)

    def test_semantic_confidence_high(self):
        text = "This is definitely the correct answer. It is absolutely proven."
        score = self.scorer.score(text)
        self.assertTrue(score > 0.6)

    def test_semantic_confidence_low(self):
        text = "Maybe this is right, but I am unsure. It could be something else."
        score = self.scorer.score(text)
        self.assertTrue(score < 0.6)

    def test_mixed_signals_explicit_wins(self):
        # Even if text sounds unsure, explicit tag should win
        text = "Maybe it is this? [CONFIDENCE: 0.9]"
        score = self.scorer.score(text)
        self.assertEqual(score, 0.9)

    def test_remove_tags(self):
        text = "Answer. [CONFIDENCE: 0.9]"
        clean = self.scorer.remove_confidence_tags(text)
        self.assertEqual(clean, "Answer.")

if __name__ == '__main__':
    unittest.main()
