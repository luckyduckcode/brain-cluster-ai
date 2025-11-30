import unittest
import asyncio
from unittest.mock import MagicMock, patch
from digital_cortex.utils.llm_neuron import LLMNeuron, NeuronPool
from digital_cortex.utils.message import Message

class TestAsyncProcessing(unittest.TestCase):
    def setUp(self):
        self.pool = NeuronPool()
        # Mock neurons
        self.n1 = LLMNeuron("n1", model="test")
        self.n2 = LLMNeuron("n2", model="test")
        
        # Mock the synchronous process method
        self.n1.process = MagicMock(return_value=Message.create("n1", "response1", 0.9))
        self.n2.process = MagicMock(return_value=Message.create("n2", "response2", 0.8))
        
        self.pool.add_neuron(self.n1)
        self.pool.add_neuron(self.n2)

    def test_async_neuron_process(self):
        async def run_test():
            msg = await self.n1.process_async("test prompt")
            return msg

        msg = asyncio.run(run_test())
        self.assertEqual(msg.content, "response1")
        self.assertEqual(msg.source, "n1")
        # Verify sync method was called
        self.n1.process.assert_called_once()

    def test_async_pool_process(self):
        async def run_test():
            msgs = await self.pool.process_parallel_async("test prompt")
            return msgs

        msgs = asyncio.run(run_test())
        self.assertEqual(len(msgs), 2)
        sources = {m.source for m in msgs}
        self.assertEqual(sources, {"n1", "n2"})
        
        # Verify both neurons were called
        self.n1.process.assert_called()
        self.n2.process.assert_called()

if __name__ == '__main__':
    unittest.main()
