import unittest
from digital_cortex.utils.cache import SemanticCache
from digital_cortex.utils.message import Message

class TestSemanticCache(unittest.TestCase):
    def setUp(self):
        self.cache = SemanticCache(max_size=3)

    def test_exact_match(self):
        # Store a response
        msg = Message.create("test", "response1", 0.9)
        self.cache.put("hello world", "model1", 0.7, msg)
        
        # Retrieve exact match
        cached = self.cache.get("hello world", "model1", 0.7)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.content, "response1")
        
        # Check stats
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 0)

    def test_similar_match(self):
        # Use lower threshold for this test
        cache = SemanticCache(max_size=10, similarity_threshold=0.7)
        
        # Store a response
        msg = Message.create("test", "response1", 0.9)
        cache.put("what is the weather today", "model1", 0.7, msg)
        
        # Similar query should hit (high word overlap)
        cached = cache.get("what is the weather", "model1", 0.7)
        self.assertIsNotNone(cached)
        
        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 1)

    def test_cache_miss(self):
        # Store a response
        msg = Message.create("test", "response1", 0.9)
        self.cache.put("hello world", "model1", 0.7, msg)
        
        # Different query should miss
        cached = self.cache.get("completely different query", "model1", 0.7)
        self.assertIsNone(cached)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats["misses"], 1)

    def test_lru_eviction(self):
        # Fill cache to capacity
        for i in range(3):
            msg = Message.create("test", f"response{i}", 0.9)
            self.cache.put(f"query {i}", "model1", 0.7, msg)
        
        self.assertEqual(self.cache.get_stats()["size"], 3)
        
        # Add one more - should evict oldest
        msg = Message.create("test", "response3", 0.9)
        self.cache.put("query 3", "model1", 0.7, msg)
        
        self.assertEqual(self.cache.get_stats()["size"], 3)
        
        # First query should be evicted
        cached = self.cache.get("query 0", "model1", 0.7)
        self.assertIsNone(cached)

    def test_different_params_no_match(self):
        # Store with one temperature
        msg = Message.create("test", "response1", 0.9)
        self.cache.put("hello", "model1", 0.7, msg)
        
        # Different temperature should miss
        cached = self.cache.get("hello", "model1", 0.5)
        self.assertIsNone(cached)

if __name__ == '__main__':
    unittest.main()
