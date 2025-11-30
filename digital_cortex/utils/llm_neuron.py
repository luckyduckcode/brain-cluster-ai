"""
LLM-Neuron: Interface for connecting local LLMs as processing neurons.

This module provides the interface between the Corpus Colosseum and local LLMs
running via Ollama. Each neuron can process inputs and generate outputs with
confidence scores.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from ..utils.message import Message
from ..utils.confidence_scorer import ConfidenceScorer
from ..utils.async_utils import async_wrap
from ..utils.cache import SemanticCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMNeuron:
    """
    A single LLM-neuron that processes inputs and generates outputs.
    
    Each neuron:
    1. Receives a prompt/task
    2. Processes it using a local LLM (via Ollama)
    3. Generates a response with confidence score
    4. Returns a Message object
    """
    
    def __init__(self, 
                 name: str,
                 model: str = "llama3.2:1b",
                 ollama_url: str = "http://localhost:11434",
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7,
                 cache: Optional[SemanticCache] = None):
        """
        Initialize an LLM-Neuron.
        
        Args:
            name: Unique identifier for this neuron
            model: Ollama model to use (e.g., "llama3.2:1b", "mistral")
            ollama_url: URL of Ollama API
            system_prompt: Optional system prompt to define neuron's role
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            cache: Optional SemanticCache instance for response caching
        """
        self.name = name
        self.model = model
        self.ollama_url = ollama_url
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.scorer = ConfidenceScorer()
        self.cache = cache
        
        logger.info(f"LLM-Neuron '{name}' initialized (model={model}, cache={'enabled' if cache else 'disabled'})")
    
    def process(self, prompt: str, extract_confidence: bool = True) -> Message:
        """
        Process a prompt and generate a response.
        
        Args:
            prompt: The input prompt/task
            extract_confidence: Whether to extract confidence from response
            
        Returns:
            Message object with response and confidence score
        """
        # Build the full prompt
        full_prompt = prompt
        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        # Add confidence extraction instruction if needed
        if extract_confidence:
            full_prompt += "\n\nIMPORTANT: At the very end of your response, on a new line, include exactly: [CONFIDENCE: X.XX] where X.XX is your confidence level from 0.0 to 1.0."
        
        # Check cache first
        if self.cache:
            cached_response = self.cache.get(full_prompt, self.model, self.temperature)
            if cached_response:
                logger.debug(f"{self.name} using cached response")
                return cached_response
        
        # Call Ollama API
        try:
            response = self._call_ollama(full_prompt)
            content = response.strip()
            
            # Extract confidence using advanced scorer
            confidence = self.scorer.score(content) if extract_confidence else 0.5
            
            # Remove confidence tag from content
            if extract_confidence:
                content = self.scorer.remove_confidence_tags(content)
            
            # Create message
            message = Message.create(
                source=self.name,
                content=content,
                confidence=confidence,
                metadata={
                    "model": self.model,
                    "temperature": self.temperature
                }
            )
            
            logger.debug(f"{self.name} generated response (confidence={confidence:.2f})")
            
            # Store in cache
            if self.cache:
                self.cache.put(full_prompt, self.model, self.temperature, message)
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing with {self.name}: {e}")
            # Return error message with low confidence
            return Message.create(
                source=self.name,
                content=f"Error: {str(e)}",
                confidence=0.0,
                metadata={"error": True}
            )

    async def process_async(self, prompt: str, extract_confidence: bool = True) -> Message:
        """
        Process a prompt asynchronously.
        
        Args:
            prompt: The input prompt/task
            extract_confidence: Whether to extract confidence from response
            
        Returns:
            Message object with response and confidence score
        """
        # Wrap the synchronous process method
        # In a real implementation, we would use aiohttp for true async I/O
        # but running requests in an executor is a good first step
        return await async_wrap(self.process)(prompt, extract_confidence)
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate response."""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    

    
    def __repr__(self) -> str:
        return f"LLMNeuron(name={self.name}, model={self.model})"


class NeuronPool:
    """Manages a pool of LLM-Neurons for parallel processing."""
    
    def __init__(self):
        self.neurons: Dict[str, LLMNeuron] = {}
        logger.info("NeuronPool initialized")
    
    def add_neuron(self, neuron: LLMNeuron):
        """Add a neuron to the pool."""
        self.neurons[neuron.name] = neuron
        logger.info(f"Added neuron '{neuron.name}' to pool")
    
    def create_neuron(self, name: str, **kwargs) -> LLMNeuron:
        """Create and add a neuron to the pool."""
        neuron = LLMNeuron(name=name, **kwargs)
        self.add_neuron(neuron)
        return neuron
    
    def process_parallel(self, prompt: str, neuron_names: Optional[List[str]] = None) -> List[Message]:
        """Process a prompt with multiple neurons (synchronous/sequential)."""
        if neuron_names:
            neurons = [self.neurons[name] for name in neuron_names if name in self.neurons]
        else:
            neurons = list(self.neurons.values())
        
        if not neurons:
            logger.warning("No neurons available")
            return []
        
        logger.info(f"Processing with {len(neurons)} neurons (sequential)")
        
        messages = []
        for neuron in neurons:
            message = neuron.process(prompt)
            messages.append(message)
        
        return messages

    async def process_parallel_async(self, prompt: str, neuron_names: Optional[List[str]] = None) -> List[Message]:
        """
        Process a prompt with multiple neurons in parallel (asynchronous).
        
        Args:
            prompt: Input prompt
            neuron_names: Optional list of specific neurons to use
            
        Returns:
            List of Message objects
        """
        import asyncio
        
        if neuron_names:
            neurons = [self.neurons[name] for name in neuron_names if name in self.neurons]
        else:
            neurons = list(self.neurons.values())
        
        if not neurons:
            logger.warning("No neurons available")
            return []
        
        logger.info(f"Processing with {len(neurons)} neurons (parallel async)")
        
        # Create tasks for all neurons
        tasks = [neuron.process_async(prompt) for neuron in neurons]
        
        # Wait for all tasks to complete
        messages = await asyncio.gather(*tasks)
        
        return list(messages)
    
    def list_neurons(self) -> List[str]:
        """List all neuron names."""
        return list(self.neurons.keys())
